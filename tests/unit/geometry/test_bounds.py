"""Analytic bounds under affine placement."""

import pytest

from pdl import Transform


def test_arc_bounds_follow_affine_extrema_without_lowering() -> None:
    from pdl import Arc
    from pdl.geometry.bounds import transformed_bounds

    arc = Arc((3, 5), 10, 4, 20, -240, rotation=35)
    transform = Transform.translate(10, 20) @ Transform.shear(0.4) @ Transform.rotate(17)
    box = transformed_bounds(arc, transform)
    samples = [
        transform.apply(arc.at(arc.start_angle + arc.sweep_angle * i / 1000)) for i in range(1001)
    ]
    assert box.left == pytest.approx(min(p.x for p in samples), abs=0.001)
    assert box.right == pytest.approx(max(p.x for p in samples), abs=0.001)
    assert box.bottom == pytest.approx(min(p.y for p in samples), abs=0.001)
    assert box.top == pytest.approx(max(p.y for p in samples), abs=0.001)
