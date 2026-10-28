"""State capture, dependency order and frame conversion contracts."""

from math import sqrt
from xml.etree import ElementTree as ET

import pytest

from pdl import (
    Canvas,
    Circle,
    Drawing,
    Group,
    Node,
    Path,
    Point,
    Rectangle,
    Style,
    Text,
    Transform,
)


def test_reference_captures_target_before_later_edit() -> None:
    canvas = Canvas(100, 60)
    a = Rectangle((0, 0), 20, 10).move_to((30, 20))
    b = Circle((0, 0), 2).move_to(a.anchor("west"))
    a.move_to((80, 30))
    assert canvas.query().point(b.anchor()) == Point(20, 20)
    assert canvas.query().point(a.anchor()) == Point(80, 30)
    assert canvas.drawings == ()


def test_draw_captures_two_independent_placements() -> None:
    canvas = Canvas(100, 60)
    b = Circle((0, 0), 2).move_to((10, 10))
    canvas.draw(b)
    b.translate(30, 0)
    canvas.draw(b)
    assert canvas.bounds(canvas.drawings[0]).anchor() == Point(10, 10)
    assert canvas.bounds(canvas.drawings[1]).anchor() == Point(40, 10)


def test_dependency_measurement_and_paint_order_are_independent() -> None:
    canvas = Canvas(100, 60)
    a = Node(Text("A"), position=(30, 20))
    b = Circle((0, 0), 2).move_to(a.anchor("west"))
    c = Node(Text("C")).move_to(a.anchor("east"))
    canvas.draw(b)
    canvas.draw(c)
    canvas.draw(a)
    output = ET.fromstring(canvas.render())[0]
    assert output[0].tag.endswith("circle")
    assert len(canvas.drawings) == 3
    assert canvas.query().point(b.anchor()).x < canvas.query().point(c.anchor()).x


def test_path_captured_at_draw_and_entity_creation() -> None:
    path = Path().move_to((10, 10)).line_to((20, 10))
    canvas = Canvas(100, 60)
    canvas.draw(path)
    entity = path.copy()
    path.line_to((90, 50))
    assert canvas.bounds(canvas.drawings[0]).right == 20
    assert canvas.bounds(entity).right == 20


def test_shape_anchor_differs_from_world_box_anchor() -> None:
    canvas = Canvas(100, 60)
    a = Rectangle((-10, -5), 20, 10).rotate(45)
    anchor = canvas.query().point(a.anchor("east"))
    box_anchor = canvas.bounds(a).anchor("east")
    assert anchor.x == pytest.approx(10 / sqrt(2))
    assert anchor.y == pytest.approx(10 / sqrt(2))
    assert box_anchor.x > anchor.x
    assert box_anchor.y == pytest.approx(0)


def test_group_moves_internal_positions_together() -> None:
    canvas = Canvas(100, 60)
    a = Rectangle((-5, -5), 10, 10)
    b = Circle((0, 0), 2).move_to(a.anchor("east"))
    group = Group((Drawing(a), Drawing(b)))
    placed = Drawing(group, transform=Transform.translate(30, 20))
    assert canvas.bounds(placed).left == 25
    assert canvas.bounds(placed).right == 37


def test_circle_affine_bounds_are_analytic() -> None:
    canvas = Canvas(100, 60)
    circle = Drawing(Circle((0, 0), 3), transform=Transform.shear(1))
    box = canvas.bounds(circle)
    assert box.right == pytest.approx(3 * sqrt(2), abs=1e-12)
    assert box.top == pytest.approx(3)


@pytest.mark.parametrize("mode", ["fit", "auto_size", "clip"])
def test_viewport_policy_and_queries_agree(mode: str) -> None:
    from typing import Literal, cast

    policy = cast(Literal["fit", "auto_size", "clip"], mode)
    canvas = Canvas(100, 60, mode=policy, padding=5)
    rect = Rectangle((200, 100), 20, 10).set_style(Style(stroke=None))
    canvas.draw(rect)
    output = ET.fromstring(canvas.render())
    box = canvas.bounds(rect)
    if mode == "fit":
        assert box.width == pytest.approx(90)
        assert box.anchor() == Point(50, 30)
    elif mode == "auto_size":
        assert output.attrib["width"] == "30mm"
        assert output.attrib["height"] == "20mm"
        assert box.left == 5
        assert box.bottom == 5
    else:
        assert box.left == 200
    assert len(canvas.drawings) == 1


def test_empty_canvas_and_invalid_fit_area() -> None:
    assert 'width="1mm"' in Canvas(mode="auto_size").render()
    canvas = Canvas(10, 10, mode="fit", padding=6)
    canvas.draw(Circle((0, 0), 2))
    with pytest.raises(ValueError, match="fitting area"):
        canvas.render()


def test_shared_mutable_path_is_frozen_in_every_occurrence() -> None:
    path = Path().move_to((10, 10)).line_to((20, 10))
    group = Group((Drawing(path), Drawing(path, transform=Transform.translate(0, 10))))
    canvas = Canvas(100, 60)
    canvas.draw(group)
    path.line_to((90, 50))
    assert canvas.bounds(canvas.drawings[0]).right == 20


def test_empty_geometry_does_not_expand_nonempty_bounds() -> None:
    canvas = Canvas(100, 60)
    group = Group((Drawing(Path()), Drawing(Rectangle((30, 20), 10, 10))))
    assert canvas.bounds(group).left == 30
    assert canvas.bounds(Path()).is_empty
    with pytest.raises(ValueError, match="Empty"):
        canvas.bounds(Path()).anchor()


def test_shared_entity_is_captured_in_every_occurrence() -> None:
    a = Circle((0, 0), 2).move_to((10, 10))
    canvas = Canvas(100, 60)
    canvas.draw(Group((Drawing(a), Drawing(a))))
    a.translate(70, 0)
    assert canvas.bounds(canvas.drawings[0]).right == 12


def test_capture_does_not_require_font_measurement(monkeypatch: pytest.MonkeyPatch) -> None:
    import pdl.rendering.config as configuration

    def unavailable() -> tuple[()]:
        raise AssertionError("Authoring must not request fonts")

    monkeypatch.setattr(configuration, "default_fonts", unavailable)
    a = Node(Text("A"))
    b = Circle((0, 0), 2).move_to(a.anchor("west"))
    canvas = Canvas(100, 60)
    canvas.draw(b)
    canvas.draw(a)
    assert len(canvas.drawings) == 2
