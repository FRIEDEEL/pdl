"""Immutable current-coordinate path command records."""

from dataclasses import dataclass

from pdl.author.geometry.point import Point


@dataclass(frozen=True)
class Move:
    """Start a subpath at an absolute position without drawing a segment."""

    end: Point


@dataclass(frozen=True)
class Segment:
    """Draw a straight segment from the current position to an absolute endpoint."""

    end: Point


@dataclass(frozen=True)
class Quadratic:
    """Draw a quadratic Bezier segment using one absolute control point."""

    control: Point
    end: Point


@dataclass(frozen=True)
class Cubic:
    """Draw a cubic Bezier segment using two absolute control points."""

    control1: Point
    control2: Point
    end: Point


@dataclass(frozen=True)
class Close:
    """Close the current subpath back to its initial Move position."""


type Command = Move | Segment | Quadratic | Cubic | Close
