"""Editable two-dimensional geometric drawing objects."""

from __future__ import annotations

from dataclasses import dataclass
from math import atan2, ceil, cos, degrees, isfinite, pi, radians, sin, sqrt, tan
from typing import Self

from pdl.author.entity import Entity
from pdl.author.measurement import layout_session
from pdl.author.references import PointSource
from pdl.foundation.geometry.primitives import Path as PathData
from pdl.foundation.geometry.primitives import Point, Position, point


class Path(PathData, Entity):
    """Editable path; commands use local coordinates and placement edits the object."""

    def move_to(self, end: PointSource) -> Self:
        """Begin a local subpath at an immediately evaluated point."""
        with layout_session() as context:
            PathData.move_to(self, context.point(end))
        return self


@dataclass(eq=False)
class Line(Entity):
    """A straight segment between two local positions in millimeters.

    Args:
        start: First endpoint.
        end: Second endpoint.
    """

    start: Position
    end: Position

    def to_path(self) -> Path:
        return Path().move_to(self.start).line_to(self.end)


@dataclass(eq=False)
class Polyline(Entity):
    """An open chain joining the supplied points in order.

    Args:
        points: Local positions in millimeters. An empty tuple draws nothing.

    Fill closes the chain implicitly; stroke does not.
    """

    points: tuple[Position, ...]

    def to_path(self) -> Path:
        if not self.points:
            return Path()
        path = Path().move_to(self.points[0])
        for p in self.points[1:]:
            path.line_to(p)
        return path


@dataclass(eq=False)
class Polygon(Polyline):
    """A closed chain joining the supplied vertices in order.

    Args:
        points: Local vertices in millimeters. The last connects to the first.
    """

    def to_path(self) -> Path:
        path = super().to_path()
        return path.close() if self.points else path


@dataclass(eq=False)
class Rectangle(Entity):
    """An axis-aligned rectangle positioned by its lower-left corner.

    Args:
        origin: Lower-left corner in local millimeters.
        width: Nonnegative horizontal extent in millimeters.
        height: Nonnegative vertical extent in millimeters.

    Raises:
        ValueError: A dimension is negative or nonfinite, or the origin is nonfinite.
    """

    origin: Position
    width: float
    height: float

    def __post_init__(self) -> None:
        if not all(isfinite(v) and v >= 0 for v in (self.width, self.height)):
            raise ValueError("Rectangle dimensions must be finite and nonnegative.")
        point(self.origin)

    def to_path(self) -> Path:
        p = point(self.origin)
        return Polygon(
            (
                (p.x, p.y),
                (p.x + self.width, p.y),
                (p.x + self.width, p.y + self.height),
                (p.x, p.y + self.height),
            )
        ).to_path()


@dataclass(eq=False)
class Arc(Entity):
    """An elliptical arc with counterclockwise-positive degree angles.

    Args:
        center: Ellipse center in local millimeters.
        radius_x: Positive local x radius in millimeters.
        radius_y: Positive local y radius in millimeters.
        start_angle: Starting ellipse parameter angle in degrees.
        sweep_angle: Signed span, at most 360 degrees in magnitude.
        rotation: Rotation of the ellipse axes in degrees.

    The parameter angle belongs to the unrotated ellipse, not the polar angle
    of the final point. Native output preserves arcs when supported;
    ``to_path`` approximates them with cubic Bezier segments.
    """

    center: Position
    radius_x: float
    radius_y: float
    start_angle: float
    sweep_angle: float
    rotation: float = 0

    def __post_init__(self) -> None:
        point(self.center)
        if not all(
            isfinite(v)
            for v in (
                self.radius_x,
                self.radius_y,
                self.start_angle,
                self.sweep_angle,
                self.rotation,
            )
        ):
            raise ValueError("Arc parameters must be finite.")
        if self.radius_x <= 0 or self.radius_y <= 0:
            raise ValueError("Arc radii must be positive.")
        if abs(self.sweep_angle) > 360:
            raise ValueError("Arc sweep must be within one revolution.")

    @classmethod
    def from_tikz(
        cls,
        start: Position,
        *,
        radius: float,
        start_angle: float,
        end_angle: float,
        radius_y: float | None = None,
    ) -> Arc:
        """Construct from a start point, radii and TikZ-style angles."""
        p = point(start)
        ry = radius if radius_y is None else radius_y
        a = radians(start_angle)
        return cls(
            (p.x - radius * cos(a), p.y - ry * sin(a)),
            radius,
            ry,
            start_angle,
            end_angle - start_angle,
        )

    @classmethod
    def from_svg(
        cls,
        start: Position,
        end: Position,
        *,
        radius_x: float,
        radius_y: float,
        rotation: float = 0,
        large_arc: bool = False,
        sweep: bool = False,
    ) -> Arc | Line | Path:
        """Use SVG endpoint parameters in pdl's Cartesian coordinate system.

        Positive sweep follows increasing ellipse angle (counterclockwise in
        pdl). Zero radii produce a line; coincident endpoints produce no arc.
        Radii are made positive and enlarged when needed, as in SVG.
        """
        p, q = point(start), point(end)
        if not all(isfinite(v) for v in (radius_x, radius_y, rotation)):
            raise ValueError("Arc parameters must be finite.")
        rx, ry = abs(radius_x), abs(radius_y)
        if p == q:
            return Path().move_to(p)
        if rx == 0 or ry == 0:
            return Line(p, q)
        phi = radians(rotation)
        c, s = cos(phi), sin(phi)
        dx, dy = (p.x - q.x) / 2, (p.y - q.y) / 2
        x, y = c * dx + s * dy, -s * dx + c * dy
        scale = max(1.0, sqrt((x / rx) ** 2 + (y / ry) ** 2))
        rx, ry = rx * scale, ry * scale
        ratio = max(0.0, (rx * ry) ** 2 - (rx * y) ** 2 - (ry * x) ** 2)
        factor = sqrt(ratio / ((rx * y) ** 2 + (ry * x) ** 2))
        if large_arc == sweep:
            factor = -factor
        cx, cy = factor * rx * y / ry, -factor * ry * x / rx
        center = (c * cx - s * cy + (p.x + q.x) / 2, s * cx + c * cy + (p.y + q.y) / 2)
        a = atan2((y - cy) / ry, (x - cx) / rx)
        b = atan2((-y - cy) / ry, (-x - cx) / rx)
        delta = (b - a) % (2 * pi)
        if not sweep:
            delta = delta - 2 * pi if delta else 0
        return cls(center, rx, ry, degrees(a), degrees(delta), rotation)

    def _transform(self, x: float, y: float) -> Point:
        p = point(self.center)
        c, s = cos(radians(self.rotation)), sin(radians(self.rotation))
        return Point(p.x + c * x - s * y, p.y + s * x + c * y)

    def at(self, angle: float) -> Point:
        """Return the ellipse point at a parameter angle in degrees."""
        a = radians(angle)
        return self._transform(self.radius_x * cos(a), self.radius_y * sin(a))

    def to_path(self) -> Path:
        """Approximate by cubic segments spanning at most 45 degrees."""
        path = Path().move_to(self.at(self.start_angle))
        count = ceil(abs(self.sweep_angle) / 45)
        if count == 0:
            return path
        step = radians(self.sweep_angle / count)
        for i in range(count):
            a = radians(self.start_angle) + i * step
            b = a + step
            k = 4 / 3 * tan(step / 4)
            p1 = self._transform(
                self.radius_x * (cos(a) - k * sin(a)),
                self.radius_y * (sin(a) + k * cos(a)),
            )
            p2 = self._transform(
                self.radius_x * (cos(b) + k * sin(b)),
                self.radius_y * (sin(b) - k * cos(b)),
            )
            path.cubic_to(p1, p2, self.at(degrees(b)))
        return path


@dataclass(eq=False)
class Circle(Entity):
    """A circle described by its center and radius.

    Args:
        center: Local center in millimeters.
        radius: Positive radius in millimeters.

    Raises:
        ValueError: The radius is nonpositive/nonfinite, or the center is nonfinite.
    """

    center: Position
    radius: float

    def __post_init__(self) -> None:
        point(self.center)
        if not isfinite(self.radius) or self.radius <= 0:
            raise ValueError("Circle radius must be positive and finite.")

    def to_path(self) -> Path:
        return Arc(self.center, self.radius, self.radius, 0, 360).to_path().close()
