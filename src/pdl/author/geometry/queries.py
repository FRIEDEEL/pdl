"""Current-state geometric queries without ownership or paint policy."""

from typing import Protocol, runtime_checkable

from pdl.author.geometry.bounds import Bounds, geometry_bounds
from pdl.author.geometry.path import Move, Path
from pdl.author.geometry.point import Point, as_point
from pdl.author.geometry.protocols import PathSource
from pdl.author.geometry.shapes import Arc, Circle, Line, Polyline, Rectangle


@runtime_checkable
class Measured(Protocol):
    @property
    def layout_bounds(self) -> Bounds: ...


@runtime_checkable
class Positioned(Protocol):
    @property
    def position(self) -> Point | tuple[float, float]: ...


def bounds_of(geometry: object) -> Bounds:
    """Return logical bounds, measuring typography only if needed."""
    if isinstance(geometry, Point):
        return Bounds(geometry.x, geometry.y, geometry.x, geometry.y)
    if isinstance(geometry, Measured):
        return geometry.layout_bounds
    if isinstance(geometry, PathSource):
        return geometry_bounds(geometry)
    raise TypeError(f"No bounds query for {type(geometry).__name__}.")


def reference_of(geometry: object) -> Point:
    """Return a cheap default pivot; never measure text to find it."""
    if isinstance(geometry, Point):
        return geometry
    if isinstance(geometry, (Circle, Arc)):
        return as_point(geometry.center)
    if isinstance(geometry, Line):
        return as_point(geometry.start)
    if isinstance(geometry, Rectangle):
        return as_point(geometry.origin)
    if isinstance(geometry, Polyline):
        return as_point(geometry.points[0]) if geometry.points else Point(0, 0)
    if isinstance(geometry, Path):
        return next((c.end for c in geometry.commands if isinstance(c, Move)), Point(0, 0))
    if isinstance(geometry, Positioned):
        return as_point(geometry.position)
    return Point(0, 0)
