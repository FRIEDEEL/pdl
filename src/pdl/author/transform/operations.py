"""Immediate geometry conversion policy shared by all drawing targets."""

from copy import copy
from dataclasses import replace
from math import atan2, degrees, hypot, isclose
from typing import Protocol, runtime_checkable

from pdl.author.geometry.frame import Frame
from pdl.author.geometry.image import Image
from pdl.author.geometry.point import Point
from pdl.author.geometry.protocols import PathSource
from pdl.author.geometry.queries import bounds_of
from pdl.author.geometry.shapes import Arc, Circle, Line, Polygon, Polyline, Rectangle
from pdl.author.geometry.tex import TeX
from pdl.author.geometry.text import Text
from pdl.author.style.gradient import LinearGradient, RadialGradient
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
    if isinstance(geometry, Frame):
        return Frame(
            transform.map(geometry.origin),
            transform.apply_vector(geometry.x_axis),
            transform.apply_vector(geometry.y_axis),
            geometry.name,
        )
    if isinstance(geometry, Image):
        result = copy(geometry)
        p, q, u, v = geometry.corners
        result.corners = (transform.map(p), transform.map(q), transform.map(u), transform.map(v))
        result.position = result.corners[0]
        return result
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
    if isinstance(geometry, (Text, TeX)):
        sx, sy = hypot(transform.a, transform.b), hypot(transform.c, transform.d)
        orthogonal = isclose(
            transform.a * transform.c + transform.b * transform.d,
            0,
            abs_tol=1e-12 * max(1.0, sx * sy),
        )
        if sx > 0 and transform.determinant > 0 and isclose(sx, sy, rel_tol=1e-12) and orthogonal:
            return replace(
                geometry,
                position=transform.map(geometry.position),
                size=geometry.size * sx,
                rotation=(geometry.rotation + degrees(atan2(transform.b, transform.a))) % 360,
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


def transform_style(
    explicit: Style | None, effective: Style, transform: Transform, geometry: object
) -> Style | None:
    """Bake paint coordinates and apply explicitly requested line-width scaling."""
    result = explicit
    fill = effective.fill
    if (
        isinstance(fill, (LinearGradient, RadialGradient))
        and isinstance(transform, AffineTransform)
        and not isinstance(geometry, Point)
        and transform != AffineTransform()
    ):
        frame = fill.frame
        if frame is None:
            box = bounds_of(geometry)
            frame = ((box.left, box.bottom), (box.right, box.bottom), (box.left, box.top))
        frame = (transform.apply(frame[0]), transform.apply(frame[1]), transform.apply(frame[2]))
        result = replace(effective, fill=replace(fill, frame=frame))
    if isinstance(transform, Rescale) and transform.include_linewidth:
        paint = effective if result is None else result
        result = replace(paint, line_width=paint.line_width * abs(transform.factor))
    return result
