"""Absolute path commands and a mutable geometric path builder."""

from __future__ import annotations

from math import hypot
from typing import TYPE_CHECKING, Self

if TYPE_CHECKING:
    from pdl.author.geometry.protocols import Mapping, PathSource
    from pdl.author.geometry.shapes import Arc

from pdl.author.geometry.bounds import Anchor, Bounds, geometry_bounds
from pdl.author.geometry.commands import (
    Close as Close,
)
from pdl.author.geometry.commands import (
    Command as Command,
)
from pdl.author.geometry.commands import (
    Cubic as Cubic,
)
from pdl.author.geometry.commands import (
    Move as Move,
)
from pdl.author.geometry.commands import (
    Quadratic as Quadratic,
)
from pdl.author.geometry.commands import (
    Segment as Segment,
)
from pdl.author.geometry.point import Point, Position, as_point


class Path:
    """A mutable sequence of absolute geometric commands, in millimeters.

    Builder methods modify this path and return it for chaining. Start each
    subpath with ``move_to`` before adding segments or closing it. ``close``
    returns the current position to that subpath's start; a subsequent segment
    continues from there. Multiple open or closed subpaths are supported.

    ``commands`` returns a tuple snapshot containing immutable commands and
    points. ``copy`` creates an independently editable path. Coordinates use
    the authoring world unless explicitly converted elsewhere. This description
    has no style, Entity state, implicit frame, or output behavior. Applying transforms,
    reference-point queries, and bounds are not implemented in this checkpoint.
    """

    def __init__(self) -> None:
        self._commands: list[Command] = []
        self._current: Point | None = None
        self._start: Point | None = None

    @property
    def commands(self) -> tuple[Command, ...]:
        """Return a read-only snapshot unaffected by subsequent builder edits."""
        return tuple(self._commands)

    @property
    def current_point(self) -> Point | None:
        """Return the current position, or None while the path is empty."""
        return self._current

    @property
    def bounds(self) -> Bounds:
        return geometry_bounds(self)

    @property
    def center(self) -> Point:
        return self.bounds.anchor()

    @property
    def reference(self) -> Point:
        return next((c.end for c in self.commands if isinstance(c, Move)), Point(0, 0))

    def anchor(self, name: Anchor = "center") -> Point:
        return self.bounds.anchor(name)

    def move_to(self, end: Position) -> Self:
        """Start a subpath at an absolute Point or pair of millimeter coordinates.

        This builds geometry; it does not reposition an existing drawing object.
        """
        position = as_point(end)
        self._commands.append(Move(position))
        self._current = self._start = position
        return self

    def _require_current(self) -> None:
        if self._current is None:
            raise ValueError("Start a subpath with move_to first.")

    def line_to(self, end: Position) -> Self:
        """Append a straight segment; require a previously started subpath.

        Args:
            end: Absolute endpoint in millimeters.

        Returns:
            This modified path.

        Raises:
            ValueError: The subpath has not started or coordinates are nonfinite.
        """
        self._require_current()
        position = as_point(end)
        self._commands.append(Segment(position))
        self._current = position
        return self

    def quadratic_to(self, control: Position, end: Position) -> Self:
        """Append a quadratic Bezier segment from the current position.

        Args:
            control: Absolute control point in millimeters.
            end: Absolute endpoint in millimeters.

        Returns:
            This modified path.

        Raises:
            ValueError: The subpath has not started or coordinates are nonfinite.
        """
        self._require_current()
        command = Quadratic(as_point(control), as_point(end))
        self._commands.append(command)
        self._current = command.end
        return self

    def cubic_to(self, control1: Position, control2: Position, end: Position) -> Self:
        """Append a cubic Bezier segment from the current position.

        Args:
            control1: First absolute control point in millimeters.
            control2: Second absolute control point in millimeters.
            end: Absolute endpoint in millimeters.

        Returns:
            This modified path.

        Raises:
            ValueError: The subpath has not started or coordinates are nonfinite.
        """
        self._require_current()
        command = Cubic(as_point(control1), as_point(control2), as_point(end))
        self._commands.append(command)
        self._current = command.end
        return self

    def close(self) -> Self:
        """Close the current subpath and return its cursor to the start.

        Raises:
            ValueError: No subpath has been started with move_to.
        """
        self._require_current()
        self._commands.append(Close())
        self._current = self._start
        return self

    def extend(self, other: PathSource) -> Self:
        """Append another path's subpaths without adding a connecting segment.

        Args:
            other: Path whose commands are captured now; later edits are independent.
                Extending with an empty path leaves this builder's cursor unchanged.

        Returns:
            This modified path. Extending with itself appends its commands once.
        """
        source = other.to_path()
        commands = source.commands
        if commands:
            self._commands.extend(commands)
            self._current, self._start = source._current, source._start
        return self

    def copy(self) -> Path:
        """Return an independent path with the same commands and builder cursor."""
        result = Path()
        result._commands = self._commands.copy()
        result._current, result._start = self._current, self._start
        return result

    def to_path(self) -> Path:
        """Return an independent current-shape snapshot."""
        return self.copy()

    def arc(self, arc: Arc) -> Self:
        """Append an arc, connecting to its start only when needed."""
        start = arc.at(arc.start_angle)
        if self._current is None:
            self.move_to(start)
        elif hypot(self._current.x - start.x, self._current.y - start.y) > 1e-10:
            self.line_to(start)
        for command in arc.to_path().commands[1:]:
            if isinstance(command, Cubic):
                self.cubic_to(command.control1, command.control2, command.end)
        return self

    def mapped(self, mapping: Mapping) -> Path:
        """Map affine control points to a new path; do not mutate this builder."""

        def mapped(p: Point) -> Point:
            return Point(*mapping.apply((p.x, p.y)))

        result = Path()
        for command in self.commands:
            match command:
                case Move(end):
                    result.move_to(mapped(end))
                case Segment(end):
                    result.line_to(mapped(end))
                case Quadratic(control, end):
                    result.quadratic_to(mapped(control), mapped(end))
                case Cubic(c1, c2, end):
                    result.cubic_to(mapped(c1), mapped(c2), mapped(end))
                case Close():
                    result.close()
        return result
