"""State capture, dependency order and frame conversion contracts."""

import pytest

from pdl import (
    WORLD,
    Canvas,
    Circle,
    CoordinateSystem,
    Entity,
    Point,
    Rectangle,
    Style,
    Transform,
)


def test_nested_spaces_and_canvas_mapping() -> None:
    root = CoordinateSystem(name="drawing")
    local = root.child(Transform.translate(10, 0) @ Transform.rotate(90))
    canvas = Canvas(100, 60)
    canvas.map(root, Transform.translate(30, 20))
    p = canvas.query().point(local.point(5, 0))
    assert (p.x, p.y) == pytest.approx((40, 25))
    assert canvas.query().point(local.point(5, 0), in_space=local) == Point(5, 0)
    v = canvas.query().vector(local.vector(5, 0))
    assert (v.x, v.y) == pytest.approx((0, 5))
    assert Canvas(100, 60).query().point(root.point(0, 0)) == Point(0, 0)


def test_entity_space_captures_placement() -> None:
    canvas = Canvas(100, 60)
    a = Entity(Rectangle((-5, -5), 10, 10)).translate(20, 10).rotate(90)
    frame = a.space
    b = Entity(Circle((0, 0), 1)).move_to(frame.point(5, 0))
    a.translate(50, 0)
    p = canvas.query().point(b.anchor())
    assert (p.x, p.y) == pytest.approx((-10, 25))


def test_default_world_mapping_applies_to_raw_and_entity_geometry() -> None:
    canvas = Canvas(100, 60)
    canvas.map(WORLD, Transform.translate(20, 10))
    raw = Circle((0, 0), 2)
    entity = Entity(raw)
    assert canvas.bounds(raw).anchor() == Point(20, 10)
    assert canvas.bounds(entity).anchor() == Point(20, 10)
    assert canvas.query().point(entity.anchor(), in_space=WORLD) == Point(0, 0)


def test_explicit_local_and_world_anchor_offsets() -> None:
    canvas = Canvas(100, 60)
    a = Entity(Rectangle((-5, -5), 10, 10)).rotate(90)
    local = a.anchor().shifted(a.space.vector(5, 0))
    world = a.anchor().shifted(WORLD.vector(5, 0))
    p = canvas.query().point(local)
    assert (p.x, p.y) == pytest.approx((0, 5))
    assert canvas.query().point(world) == Point(5, 0)


def test_canvas_point_round_trip_to_authoring() -> None:
    canvas = Canvas(100, 60, mode="fit", padding=5)
    a = Entity(Rectangle((30, 20), 20, 10), style=Style(stroke=None))
    canvas.draw(a)
    tip = canvas.query().point(a.anchor("east"))
    original = canvas.query().from_canvas(tip)
    assert (original.x, original.y) == pytest.approx((50, 25))
