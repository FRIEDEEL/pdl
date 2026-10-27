"""Editable groups preserve world placement, style, and captured records."""

import pytest

from pdl import Canvas, Circle, Color, Drawing, Entity, Group, Point, Style, Transform


def center(canvas: Canvas, member: Entity | Group) -> Point:
    return canvas.query().point(member.anchor())


def test_reparent_remove_and_dismiss_preserve_world_and_styles() -> None:
    canvas = Canvas(100, 100)
    red = Style(fill=Color(1, 0, 0))
    a = Entity(Circle((10, 10), 2))
    first = Group((a,), style=red).rotate(30).translate(20, 10)
    before = center(canvas, a)
    second = Group(transform=Transform.translate(40, 0))
    second.add(a)
    assert first.members == ()
    assert center(canvas, a).x == pytest.approx(before.x)
    assert center(canvas, a).y == pytest.approx(before.y)
    assert a.snapshot().placed().style == red
    second.remove(a)
    assert a.parent is None
    assert center(canvas, a).x == pytest.approx(before.x)
    second.add(a)
    assert second.dismiss() == (a,)
    assert a.parent is None
    assert a.snapshot().placed().style == red
    with pytest.raises(ValueError, match="dismissed"):
        second.add(a)


def test_nested_dismiss_preserves_child_order_and_group_identity() -> None:
    a, b, c = (Entity(Circle((x, 10), 1)) for x in (10, 20, 30))
    inner = Group((a, b)).translate(5, 0)
    outer = Group((inner, c)).rotate(90)
    before = Canvas(100, 100).bounds(outer)
    inner.dismiss()
    assert outer.members == (a, b, c)
    assert a.parent is outer
    assert Canvas(100, 100).bounds(outer) == before


def test_cycles_and_captured_group_state() -> None:
    a = Entity(Circle((10, 10), 1))
    inner = Group((a,))
    outer = Group((inner,))
    with pytest.raises(ValueError, match="Cyclic"):
        inner.add(outer)
    canvas = Canvas(100, 100)
    reference = outer.anchor()
    canvas.draw(outer)
    outer.translate(30, 0)
    assert canvas.bounds(canvas.drawings[0]).anchor() == Point(10, 10)
    assert canvas.query().point(reference) == Point(10, 10)
    with pytest.raises(ValueError, match="outermost"):
        canvas.draw(a)


def test_drawing_definitions_create_independent_instances() -> None:
    source = Entity(Circle((0, 0), 1))
    group = Group((Drawing(source), Drawing(source)))
    assert group.members[0] is not group.members[1]
    group.translate(20, 0)
    assert center(Canvas(100, 100), source) == Point(0, 0)


def test_member_move_to_and_explicit_paint_in_transformed_parent() -> None:
    canvas = Canvas(100, 100)
    explicit = Style(fill=Color(0, 0, 1))
    child = Entity(Circle((10, 10), 2), style=explicit)
    group = Group((child,), style=Style(fill=Color(1, 0, 0))).rotate(45)
    child.move_to((40, 30))
    assert center(canvas, child).x == pytest.approx(40)
    assert center(canvas, child).y == pytest.approx(30)
    assert child.snapshot().placed().style is explicit
    group.dismiss()
    assert child.snapshot().placed().style is explicit


def test_transformed_description_child_keeps_group_default_paint() -> None:
    red = Style(fill=Color(1, 0, 0))
    group = Group((Drawing(Circle((0, 0), 1)),), style=red)
    placed = Drawing(group.transformed(Transform.translate(10, 0)))
    assert placed.child(0).style is red
