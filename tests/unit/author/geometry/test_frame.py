"""Explicit frame conversion, child baking, and singular inverse rejection."""

import pytest

from pdl.author.geometry.frame import Frame
from pdl.author.geometry.point import Point, Vector
from pdl.author.transform.affine import Rotation


def test_frame_points_and_vectors_are_explicit_and_immediate() -> None:
    frame = Frame((2, 3), Vector(2, 0), Vector(0, 4))
    assert frame.point((1, 2)) == Point(4, 11)
    assert frame.vector((1, 2)) == Vector(2, 8)
    assert frame.coordinates((4, 11)) == Point(1, 2)
    child = frame.child(Rotation(90))
    assert child.point((1, 0)).x == pytest.approx(2)
    assert child.point((1, 0)).y == pytest.approx(7)
    with pytest.raises(ValueError):
        Frame(x_axis=Vector(0, 0)).coordinates((1, 2))
