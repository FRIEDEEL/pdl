"""Coordinate validation and immutable Point values."""

from dataclasses import FrozenInstanceError

import pytest

from pdl.author.geometry.point import Point, as_point


def test_coordinates_and_normalization() -> None:
    value = Point(-2.5, 3)
    assert (value.x, value.y) == (-2.5, 3)
    assert as_point(value) is value
    assert as_point((-2.5, 3)) == value


@pytest.mark.parametrize("value", [float("nan"), float("inf"), -float("inf")])
@pytest.mark.parametrize("axis", ["x", "y"])
def test_nonfinite_coordinates_are_rejected(value: float, axis: str) -> None:
    coordinates = (value, 0) if axis == "x" else (0, value)
    with pytest.raises(ValueError, match="finite"):
        as_point(coordinates)


def test_point_values_cannot_be_changed() -> None:
    value = Point(1, 2)
    with pytest.raises(FrozenInstanceError):
        setattr(value, "x", 5)
