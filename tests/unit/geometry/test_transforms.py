"""Affine composition and path transformation behavior."""

import pytest

from pdl import Circle, Line, Path
from pdl.geometry.bounds import geometry_bounds
from pdl.geometry.primitives import Point
from pdl.geometry.transforms import Transform, transform_path
from pdl.scene.composition import Drawing, Group, bounds


def test_affine_order_and_reuse() -> None:
    original = Group((Drawing(Line((0, 0), (2, 0))),))
    placed = original.transformed(Transform.translate(10, 5) @ Transform.rotate(90))
    assert bounds(original).anchor("east") == Point(2, 0)
    p = bounds(placed).anchor("north")
    assert (p.x, p.y) == pytest.approx((10, 7))
    assert bounds(original).width == 2


def test_curve_bounds_use_extrema_not_control_hull() -> None:
    quadratic = Path().move_to((0, 0)).quadratic_to((5, 10), (10, 0))
    cubic = Path().move_to((0, 0)).cubic_to((0, 10), (10, 10), (10, 0))
    assert geometry_bounds(quadratic).top == pytest.approx(5)
    assert geometry_bounds(cubic).top == pytest.approx(7.5)


def test_nested_group_bounds() -> None:
    inner = Group((Drawing(Circle((0, 0), 2)),), Transform.scale(2))
    outer = Group((Drawing(inner),), Transform.translate(10, 20))
    box = bounds(outer)
    assert (box.left, box.bottom, box.right, box.top) == pytest.approx((6, 16, 14, 24))


def test_reflection_and_nonuniform_scale() -> None:
    path = transform_path(Line((1, 2), (3, 4)), Transform.scale(-2, 3))
    box = geometry_bounds(path)
    assert (box.left, box.bottom, box.right, box.top) == (-6, 6, -2, 12)


def test_placed_circles_keep_native_output_when_possible() -> None:
    from pdl import Canvas

    circle = Circle((0, 0), 2)
    canvas = Canvas(40, 20)
    canvas.draw(Group((Drawing(circle),), Transform.translate(10, 10) @ Transform.scale(2)))
    assert "<circle" in canvas.render()
    assert "circle[radius=4mm]" in canvas.render("tikz")
    canvas = Canvas(40, 20)
    canvas.draw(Group((Drawing(circle),), Transform.scale(2, 1)))
    assert "<path" in canvas.render()
