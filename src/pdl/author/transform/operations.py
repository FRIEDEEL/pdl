"""Immediate geometry conversion policy shared by all drawing targets."""

from copy import copy
from dataclasses import replace
from math import hypot, isclose
from typing import Protocol, runtime_checkable

from pdl.author.geometry.point import Point
from pdl.author.geometry.protocols import PathSource
from pdl.author.geometry.shapes import Arc, Circle, Line, Polygon, Polyline, Rectangle
from pdl.author.geometry.tex import TeX
from pdl.author.geometry.text import Text
from pdl.author.style.style import Style
from pdl.author.transform.affine import AffineTransform, Rescale
from pdl.author.transform.base import Transform


@runtime_checkable
class Relocatable(Protocol):
    position: Point | tuple[float, float]


def transform_geometry(geometry: object, transform: Transform) -> object:
    """Return current transformed coordinates, retaining no mapping history.

    Unknown nonlinear transforms are rejected for curves: mapping their control
    points would silently change their meaning. Specialized mappings can extend
    this function with a deliberate approximation policy in the future.
    """
    if isinstance(geometry, Point):
        return Point(*transform.apply((geometry.x, geometry.y)))
    if not isinstance(transform, AffineTransform):
        raise TypeError("This geometry currently requires an affine transform.")
    if transform == AffineTransform():
        return geometry
    if isinstance(geometry, Circle):
        sx, sy = hypot(transform.a, transform.b), hypot(transform.c, transform.d)
        orthogonal = isclose(
            transform.a * transform.c + transform.b * transform.d,
            0,
            abs_tol=1e-12 * max(1.0, sx * sy),
        )
        if sx > 0 and isclose(sx, sy, rel_tol=1e-12) and orthogonal:
            return Circle(transform.map(geometry.center), geometry.radius * sx)
        return geometry.to_path().mapped(transform)
    if isinstance(geometry, Line):
        return Line(transform.map(geometry.start), transform.map(geometry.end))
    if isinstance(geometry, Rectangle):
        if transform.b == 0 and transform.c == 0 and transform.a >= 0 and transform.d >= 0:
            return Rectangle(
                transform.map(geometry.origin),
                geometry.width * transform.a,
                geometry.height * transform.d,
            )
        return geometry.to_path().mapped(transform)
    if isinstance(geometry, Polygon):
        return Polygon(tuple(transform.map(p) for p in geometry.points))
    if isinstance(geometry, Polyline):
        return Polyline(tuple(transform.map(p) for p in geometry.points))
    if isinstance(geometry, Arc):
        return geometry.to_path().mapped(transform)
    if (
        isinstance(geometry, (Text, TeX))
        and transform.b == 0
        and transform.c == 0
        and transform.a == transform.d
        and transform.a > 0
    ):
        return replace(
            geometry, position=transform.map(geometry.position), size=geometry.size * transform.a
        )
    # A translation preserves native text/TeX without measuring or outlining it.
    if isinstance(geometry, Relocatable) and (
        transform.a,
        transform.b,
        transform.c,
        transform.d,
    ) == (1, 0, 0, 1):
        result = copy(geometry)
        result.position = transform.map(geometry.position)
        return result
    if isinstance(geometry, PathSource):
        return geometry.to_path().mapped(transform)
    raise TypeError(f"No transform conversion for {type(geometry).__name__}.")


def transform_style(explicit: Style | None, effective: Style, transform: Transform) -> Style | None:
    """Apply the operation's explicit paint policy independently of geometry."""
    if isinstance(transform, Rescale) and transform.include_linewidth:
        return replace(effective, line_width=effective.line_width * abs(transform.factor))
    return explicit
