"""Snapshot isolation, effective paint, and layer ordering under the new model."""

import pytest

from pdl import Canvas, Circle, Color, Font, Gather, Group, Style, Text
from pdl.author.geometry.point import Point
from pdl.author.geometry.shapes import Circle as CircleGeometry
from pdl.author.geometry.text import Text as TextGeometry
from pdl.canvas.layers import Layer


def test_add_captures_current_state_and_style_fallback() -> None:
    member = Circle((5, 5), 2)
    group = Group(member, style=Style(line_width=3))
    canvas = Canvas(30, 20).add(group)
    group.translate(10, 0).set_style(Style(line_width=7))
    first = canvas.drawings[0]
    assert isinstance(first, Group)
    assert first.members[0].reference == Point(5, 5)
    assert first.members[0].effective_style.line_width == 3
    assert member.style is None
    canvas.add(group)
    assert 'cx="15"' in canvas.render()
    assert 'cx="5"' in canvas.render()


def test_draw_rejects_bare_geometry_and_selection() -> None:
    canvas = Canvas(20, 20)
    with pytest.raises(TypeError):
        canvas.draw(CircleGeometry((0, 0), 1))  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        canvas.draw(Gather(Circle()))  # type: ignore[arg-type]
    group = Group(Circle())
    with pytest.raises(ValueError):
        canvas.draw(group.members[0])


def test_native_text_keeps_captured_font_and_layout(font: Font) -> None:
    text = Text("Editable label", font, position=(3, 4))
    canvas = Canvas(50, 20).add(text)
    assert isinstance(text.geometry, TextGeometry)
    text.geometry.text = "Changed"
    assert "Editable label</text>" in canvas.render()
    assert "Changed" not in canvas.render()
    assert "controls" not in canvas.render("tikz")


def test_layers_reorder_captures_by_identity() -> None:
    low, high = Layer(), Layer(1)
    a, b = Circle((1, 1), 1), Circle((10, 1), 1)
    low.add(a)
    high.add(b)
    canvas = Canvas(30, 20).add(b, a)
    assert canvas.drawings[0].reference == Point(1, 1)
    canvas.layers.move_above(low, high)
    assert canvas.drawings[0].reference == Point(10, 1)
    assert low.to_gather().members == (a,)


def test_auto_size_and_fit_preserve_stroke_width() -> None:
    circle = Circle((20, 30), 2, style=Style(line_width=0.5, line_join="round"))
    auto = Canvas(mode="auto_size", padding=2).add(circle)
    page = auto.viewport()
    assert page.width > 8
    assert page.height > 8
    fit = Canvas(100, 50, mode="fit", padding=2).add(circle)
    leaf = fit.viewport().drawings[0]
    assert leaf.effective_style.line_width == 0.5
    assert leaf.center.x == pytest.approx(50)
    assert leaf.center.y == pytest.approx(25)


def test_draw_override_preserves_explicit_member_paint() -> None:
    inherited = Circle((1, 1), 1)
    explicit = Circle((5, 1), 1, style=Style(line_width=2))
    group = Group(inherited, explicit, style=Style(line_width=3))
    canvas = Canvas(30, 20)
    canvas.draw(group, Style(line_width=8))
    captured = canvas.drawings[0]
    assert isinstance(captured, Group)
    assert captured.members[0].effective_style.line_width == 8
    assert captured.members[1].effective_style.line_width == 2
    assert inherited.style is None
    assert group.style is not None and group.style.line_width == 3


def test_snapshot_layout_survives_later_font_discovery_failure(
    font: Font, monkeypatch: pytest.MonkeyPatch
) -> None:
    from pdl import Node
    from pdl.author.geometry.frame import WORLD

    canvas = Canvas(80, 30, fonts=(font,))
    captured = canvas.snapshot(Node(Text("Fixed metrics")))
    before = captured.bounds

    def unavailable() -> tuple[Font, ...]:
        raise AssertionError("Captured typography must not rediscover fonts.")

    monkeypatch.setattr("pdl.author.style.typography.default_fonts", unavailable)
    monkeypatch.setattr("pdl.author.geometry.text.default_fonts", unavailable)
    other = Canvas(80, 30).add(captured)
    assert other.query().bounds(captured, in_space=WORLD) == before
    assert "Fixed metrics" in other.render()


def test_ink_query_is_distinct_from_logical_layout(font: Font) -> None:
    canvas = Canvas(80, 30)
    text = Text(" x ", font)
    assert canvas.query().ink_bounds(text).width < canvas.query().bounds(text).width


def test_snapshot_preserves_none_members_and_editable_group_fallback() -> None:
    inherited = Circle((3, 3), 1)
    explicit = Circle((8, 3), 1, style=Style(line_width=2))
    group = Group(inherited, explicit, style=Style(line_width=3))
    snapshot = Canvas(20, 20).snapshot(group)
    assert isinstance(snapshot, Group)
    assert snapshot.members[0].style is None
    snapshot.set_style(Style(line_width=7))
    assert snapshot.members[0].effective_style.line_width == 7
    assert snapshot.members[1].effective_style.line_width == 2
    assert inherited.effective_style.line_width == 3
    rendered = Canvas(20, 20).add(snapshot).render()
    assert 'stroke-width="7"' in rendered
    assert 'stroke-width="2"' in rendered
    member = snapshot.members[0]
    snapshot.remove(member)
    assert member.style is None
    assert member.effective_style.line_width == 1


def test_snapshot_fixes_defaults_without_materializing_member_styles(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from pdl import Entity
    from pdl.author.geometry.shapes import Circle as CircleGeometry

    group = Group(Circle((3, 3), 1), Text("Default", position=(8, 3)))
    snapshot = Canvas(30, 20).snapshot(group)
    assert isinstance(snapshot, Group)
    assert snapshot.style is None
    assert all(member.style is None for member in snapshot.members)
    before = Canvas(30, 20).add(snapshot).render()
    monkeypatch.setitem(Entity.geometry_defaults, CircleGeometry, Style(line_width=9))
    assert Canvas(30, 20).add(snapshot).render() == before


def test_native_text_uses_edited_snapshot_group_fallback(font: Font) -> None:
    group = Group(
        Text("Inherited native text", font, position=(3, 8)),
        style=Style(stroke=None, fill=Color(0, 1, 0)),
    )
    snapshot = Canvas(60, 20).snapshot(group)
    snapshot.set_style(Style(stroke=None, fill=Color(0, 0, 1), opacity=0.25))
    assert isinstance(snapshot, Group)
    assert snapshot.members[0].style is None
    canvas = Canvas(60, 20).add(snapshot)
    assert 'fill="rgb(0%,0%,100%)"' in canvas.render()
    assert 'opacity="0.25"' in canvas.render()
    assert "blue,1" in canvas.render("tikz")
    assert "text opacity=0.25" in canvas.render("tikz")


def test_unsubmitted_query_predicts_fit_and_viewport_exposes_its_mapping() -> None:
    shape = Circle((100, 200), 10, style=Style(line_width=0))
    canvas = Canvas(100, 60, mode="fit", padding=5)
    before = canvas.query().bounds(shape)
    assert before.width == pytest.approx(50)
    assert before.height == pytest.approx(50)
    assert before.anchor().x == pytest.approx(50)
    assert before.anchor().y == pytest.approx(30)
    assert canvas.drawings == ()
    view = canvas.viewport((canvas.snapshot(shape),))
    assert view.output_transform.map(shape.center).x == pytest.approx(50)
    canvas.add(shape)
    assert canvas.query().bounds(shape) == before
