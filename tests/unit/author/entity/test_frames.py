"""Pure frames and explicitly created drawing axes remain distinct."""

import pytest

from pdl import Canvas, Circle, Frame, Gather, Point, frame_axes


def test_explicit_axes_transform_the_current_basis_and_visual_members() -> None:
    frame = Frame((5, 6))
    axes = frame_axes(frame, length=10)
    box = Circle((5, 6), 2)
    Gather(box, axes).rotate(90, origin=(5, 6))
    p = axes.point((1, 0))
    assert (p.x, p.y) == pytest.approx((5, 7))
    assert frame.point((1, 0)) == Point(6, 6)
    assert not hasattr(box, "frame")
    assert "<svg" in Canvas(30, 30).add(axes, box).render()


def test_axes_validate_display_dimensions() -> None:
    with pytest.raises(ValueError):
        frame_axes(Frame(), length=0)
