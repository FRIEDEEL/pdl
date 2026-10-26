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


def placed_geometry(geometry: Geometry, transform: Transform) -> Geometry:
    """Preserve native shape identity where placement has an exact equivalent."""
    from math import hypot, isclose

    from pdl.geometry import Arc, Circle, Line, Rectangle

    if transform == Transform():
        return geometry
    if isinstance(geometry, Line):
        return Line(transform.apply(geometry.start), transform.apply(geometry.end))
    if isinstance(geometry, Circle):
        xscale = hypot(transform.a, transform.b)
        yscale = hypot(transform.c, transform.d)
        perpendicular = isclose(
            transform.a * transform.c + transform.b * transform.d, 0, abs_tol=1e-12
        )
        if xscale > 0 and perpendicular and isclose(xscale, yscale, rel_tol=1e-12):
            return Circle(transform.apply(geometry.center), geometry.radius * xscale)
    if isinstance(geometry, Rectangle) and transform.b == transform.c == 0:
        origin = point(geometry.origin)
        first = transform.apply(origin)
        last = transform.apply((origin.x + geometry.width, origin.y + geometry.height))
        return Rectangle(
            (min(first.x, last.x), min(first.y, last.y)),
            abs(last.x - first.x),
            abs(last.y - first.y),
        )
    if isinstance(geometry, Arc) and (transform.a, transform.b, transform.c, transform.d) == (
        1,
        0,
        0,
        1,
    ):
        return Arc(
            transform.apply(geometry.center),
            geometry.radius_x,
            geometry.radius_y,
            geometry.start_angle,
            geometry.sweep_angle,
            geometry.rotation,
        )
    return transform_path(geometry, transform)
