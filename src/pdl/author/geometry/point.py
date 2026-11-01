"""Finite Cartesian point values without implicit coordinate frames."""

from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True)
class Point:
    """An immutable position in Cartesian drawing coordinates, in millimeters.

    Coordinates use the authoring world unless explicitly converted elsewhere.
    A Point stores no frame, style, placement matrix, or drawing relationship.

    Args:
        x: Finite horizontal coordinate; positive points right.
        y: Finite vertical coordinate; positive points up.

    Raises:
        ValueError: Either coordinate is infinite or NaN.
    """

    x: float
    y: float

    def __post_init__(self) -> None:
        if not isfinite(self.x) or not isfinite(self.y):
            raise ValueError("Point coordinates must be finite.")


type Position = Point | tuple[float, float]


def as_point(value: Position) -> Point:
    """Normalize a Point or coordinate pair without assigning a coordinate frame.

    Args:
        value: An existing Point or a pair of finite millimeter coordinates.

    Returns:
        The existing immutable Point, or a new Point constructed from the pair.

    Raises:
        ValueError: Either coordinate is infinite or NaN.
    """
    return value if isinstance(value, Point) else Point(*value)
