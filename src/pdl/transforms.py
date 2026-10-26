"""Immutable affine transformations in Cartesian millimeter coordinates."""

from __future__ import annotations

from dataclasses import dataclass
from math import cos, isfinite, radians, sin

from pdl.geometry import (
    Close,
    Cubic,
    Geometry,
    Move,
    Path,
    Point,
    Position,
    Quadratic,
    Segment,
    point,
)


@dataclass(frozen=True)
class Transform:
    """A 2D affine matrix; ``a @ b`` applies b first, then a."""

    a: float = 1
    b: float = 0
    c: float = 0
    d: float = 1
    e: float = 0
    f: float = 0

    def __post_init__(self) -> None:
        if not all(isfinite(v) for v in self.values):
            raise ValueError("Transform entries must be finite.")

    @property
    def values(self) -> tuple[float, float, float, float, float, float]:
        return self.a, self.b, self.c, self.d, self.e, self.f

    def apply(self, position: Position) -> Point:
        p = point(position)
        return Point(self.a * p.x + self.c * p.y + self.e, self.b * p.x + self.d * p.y + self.f)

    def __matmul__(self, other: Transform) -> Transform:
        return Transform(
            self.a * other.a + self.c * other.b,
            self.b * other.a + self.d * other.b,
            self.a * other.c + self.c * other.d,
            self.b * other.c + self.d * other.d,
            self.a * other.e + self.c * other.f + self.e,
            self.b * other.e + self.d * other.f + self.f,
        )

    @classmethod
    def translate(cls, x: float, y: float) -> Transform:
        return cls(e=x, f=y)

    @classmethod
    def rotate(cls, angle: float) -> Transform:
        c, s = cos(radians(angle)), sin(radians(angle))
        return cls(c, s, -s, c)

    @classmethod
    def scale(cls, x: float, y: float | None = None) -> Transform:
        return cls(a=x, d=x if y is None else y)


def transform_path(geometry: Geometry, transform: Transform) -> Path:
    """Transform geometry while leaving paint, including line width, unchanged."""
    path = Path()
    for command in geometry.to_path().commands:
        match command:
            case Move(end):
                path.move_to(transform.apply(end))
            case Segment(end):
                path.line_to(transform.apply(end))
            case Quadratic(control, end):
                path.quadratic_to(transform.apply(control), transform.apply(end))
            case Cubic(c1, c2, end):
                path.cubic_to(transform.apply(c1), transform.apply(c2), transform.apply(end))
            case Close():
                path.close()
    return path
