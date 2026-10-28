"""Exact native-shape placement optimizations for output adapters."""

from pdl.foundation.geometry.primitives import Geometry, point
from pdl.foundation.geometry.transforms import Transform, transform_path


def placed_geometry(geometry: Geometry, transform: Transform) -> Geometry:
    """Preserve native shape identity where placement has an exact equivalent."""
    from math import hypot, isclose

    from pdl.author.shapes import Arc, Circle, Line, Rectangle

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
