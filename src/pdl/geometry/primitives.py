"""Backend-independent geometry and path construction."""

from __future__ import annotations

from dataclasses import dataclass
from math import atan2, ceil, cos, degrees, hypot, isfinite, pi, radians, sin, sqrt, tan
from typing import Protocol, Self


@dataclass(frozen=True)
class Point:
    """A position in Cartesian drawing coordinates."""

    x: float
    y: float

    def __post_init__(self) -> None:
        if not all(isfinite(v) for v in (self.x, self.y)):
            raise ValueError("Coordinates must be finite.")


@dataclass(frozen=True)
class Vector:
    """A displacement, independent of coordinate origin."""

    x: float
    y: float

    def __post_init__(self) -> None:
        if not all(isfinite(v) for v in (self.x, self.y)):
            raise ValueError("Vector components must be finite.")


type Position = Point | tuple[float, float]


def point(value: Position) -> Point:
    """Convert a coordinate pair to a point."""
    return value if isinstance(value, Point) else Point(*value)


@dataclass(frozen=True)
class Move:
    end: Point


@dataclass(frozen=True)
class Segment:
    end: Point


@dataclass(frozen=True)
class Quadratic:
    control: Point
    end: Point


@dataclass(frozen=True)
class Cubic:
    control1: Point
    control2: Point
    end: Point


@dataclass(frozen=True)
class Close:
    pass


type Command = Move | Segment | Quadratic | Cubic | Close


class Geometry(Protocol):
    """Geometry that can lower to an independent path snapshot."""

    def to_path(self) -> Path: ...


class Path:
    """A mutable builder for absolute line, curve, and arc commands.

    Call ``move_to`` before adding lines or Bezier curves. Builder methods
    modify this path and return it for chaining. ``Canvas.draw`` captures a
    copy; later edits do not change a previously recorded drawing.

    A fill implicitly closes open subpaths, but their strokes remain open.
    Call ``close`` when the closing edge should also be stroked.
    """

    def __init__(self) -> None:
        self._commands: list[Command] = []
        self._current: Point | None = None
        self._start: Point | None = None

    @property
    def commands(self) -> tuple[Command, ...]:
        return tuple(self._commands)

    def move_to(self, end: Position) -> Self:
        """Start a new subpath without drawing a connecting line.

        Args:
            end: New current point in local millimeters.

        Returns:
            This path for chaining.
        """
        self._current = self._start = point(end)
        self._commands.append(Move(self._current))
        return self

    def _require_current(self) -> Point:
        if self._current is None:
            raise ValueError("Start a subpath with move_to first.")
        return self._current

    def line_to(self, end: Position) -> Self:
        """Add a straight segment from the current point.

        Args:
            end: Segment endpoint in local millimeters.

        Returns:
            This path for chaining.

        Raises:
            ValueError: No subpath has been started with ``move_to``.
        """
        self._require_current()
        self._current = point(end)
        self._commands.append(Segment(self._current))
        return self

    def quadratic_to(self, control: Position, end: Position) -> Self:
        """Add a quadratic Bezier curve with one control point.

        Args:
            control: Point controlling the endpoint tangents.
            end: Curve endpoint. Coordinates are local millimeters.

        Returns:
            This path for chaining.

        Raises:
            ValueError: No subpath has been started.
        """
        self._require_current()
        self._current = point(end)
        self._commands.append(Quadratic(point(control), self._current))
        return self

    def cubic_to(self, control1: Position, control2: Position, end: Position) -> Self:
        """Add a cubic Bezier curve with two control points.

        Args:
            control1: Control point determining the initial tangent.
            control2: Control point determining the final tangent.
            end: Curve endpoint. All coordinates are local millimeters.

        Returns:
            This path for chaining.

        Raises:
            ValueError: No subpath has been started.
        """
        self._require_current()
        self._current = point(end)
        self._commands.append(Cubic(point(control1), point(control2), self._current))
        return self

    def close(self) -> Self:
        """Close the current subpath with a straight edge.

        The current point returns to the subpath's starting point.

        Returns:
            This path for chaining.

        Raises:
            ValueError: No subpath has been started.
        """
        self._require_current()
        self._commands.append(Close())
        self._current = self._start
        return self

    def arc(self, arc: Arc) -> Self:
        """Append an arc, connecting to its start when necessary."""
        start = arc.at(arc.start_angle)
        if self._current is None:
            self.move_to(start)
        elif hypot(self._current.x - start.x, self._current.y - start.y) > 1e-10:
            self.line_to(start)
        for command in arc.to_path().commands[1:]:
            if isinstance(command, Cubic):
                self.cubic_to(command.control1, command.control2, command.end)
        return self

    def extend(self, geometry: Geometry) -> Self:
        """Append independent subpaths without connecting their start points."""
        for command in geometry.to_path().commands:
            match command:
                case Move(end):
                    self.move_to(end)
                case Segment(end):
                    self.line_to(end)
                case Quadratic(control, end):
                    self.quadratic_to(control, end)
                case Cubic(c1, c2, end):
                    self.cubic_to(c1, c2, end)
                case Close():
                    self.close()
        return self

    def to_path(self) -> Path:
        """Return an independent copy of this path's commands and current point."""
        result = Path()
        result._commands = self._commands.copy()
        result._current, result._start = self._current, self._start
        return result


@dataclass(frozen=True)
class Line:
    """A straight segment between two local positions in millimeters.

    Args:
        start: First endpoint.
        end: Second endpoint.
    """

    start: Position
    end: Position

    def to_path(self) -> Path:
        return Path().move_to(self.start).line_to(self.end)


@dataclass(frozen=True)
class Polyline:
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


@dataclass(frozen=True)
class Polygon(Polyline):
    """A closed chain joining the supplied vertices in order.

    Args:
        points: Local vertices in millimeters. The last connects to the first.
    """

    def to_path(self) -> Path:
        path = super().to_path()
        return path.close() if self.points else path


@dataclass(frozen=True)
class Rectangle:
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


@dataclass(frozen=True)
class Arc:
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


@dataclass(frozen=True)
class Circle:
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
