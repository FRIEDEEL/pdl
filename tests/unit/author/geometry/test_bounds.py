"""Analytic bounds and empty/point behavior."""

import pytest

from pdl.author.geometry.bounds import Bounds, geometry_bounds, transformed_bounds
from pdl.author.geometry.path import Path
from pdl.author.geometry.shapes import Arc, Circle
from pdl.author.transform.affine import Rotation, Shear, Translation


def test_arc_bounds_preserve_exact_transformed_extrema() -> None:
    arc = Arc((3, 5), 10, 4, 20, -240, rotation=35)
    transform = Translation(10, 20) @ Shear(0.4) @ Rotation(17)
    box = transformed_bounds(arc, transform)
    samples = [
        transform.apply((p.x, p.y))
        for p in [arc.at(arc.start_angle + arc.sweep_angle * i / 1000) for i in range(1001)]
    ]
    assert box.left == pytest.approx(min(p[0] for p in samples), abs=0.001)
    assert box.right == pytest.approx(max(p[0] for p in samples), abs=0.001)
    assert box.bottom == pytest.approx(min(p[1] for p in samples), abs=0.001)
    assert box.top == pytest.approx(max(p[1] for p in samples), abs=0.001)


def test_circle_bounds_are_not_cubic_approximations() -> None:
    box = geometry_bounds(Circle((3, 4), 2))
    assert box == Bounds(1, 2, 5, 6)


def test_cubic_bounds_follow_curve_rather_than_control_polygon() -> None:
    box = geometry_bounds(Path().move_to((0, 0)).cubic_to((0, 4), (4, 4), (4, 0)))
    assert box == Bounds(0, 0, 4, 3)
    assert geometry_bounds(Path()).is_empty
    with pytest.raises(ValueError):
        Bounds.empty().anchor()
