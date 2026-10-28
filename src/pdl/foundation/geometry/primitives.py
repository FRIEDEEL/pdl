"""Backend-independent geometry and path construction."""

from __future__ import annotations

from dataclasses import dataclass
from math import hypot, isfinite
from typing import Protocol, Self


@dataclass(frozen=True)
class Point:
    """A position in Cartesian drawing coordinates."""

    x: float
    y: float

    def __post_init__(self) -> None:
        if not all(isfinite(v) for v in (self.x, self.y)):
            raise ValueError("Coordinates must be finite.")

    def __add__(self, offset: Point | Vector | tuple[float, float]) -> Point:
        """Return a fixed point displaced by numerical coordinates."""
        p = offset if isinstance(offset, Vector) else point(offset)
        return Point(self.x + p.x, self.y + p.y)


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


class ArcGeometry(Geometry, Protocol):
    """Numerical interface for appending an elliptical arc."""

    start_angle: float

    def at(self, angle: float) -> Point: ...


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

    # Path.move_to keeps its established builder meaning; use place() for placement.
    def move_to(self, end: Position) -> Self:  # pyright: ignore[reportIncompatibleMethodOverride]
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

    def arc(self, arc: ArcGeometry) -> Self:
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
