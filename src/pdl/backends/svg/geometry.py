"""SVG output with native shapes and path fallback."""

from math import ceil

from pdl.author.geometry.base import Geometry
from pdl.author.geometry.path import (
    Close,
    Cubic,
    Move,
    Quadratic,
    Segment,
)
from pdl.author.geometry.point import as_point as point
from pdl.author.geometry.protocols import PathSource
from pdl.author.geometry.shapes import Arc, Circle, Rectangle
from pdl.author.style import Color, Style
from pdl.backends.formatting import number


def color(value: Color | None) -> str:
    if value is None:
        return "none"
    return (
        "rgb(" + ",".join(f"{number(v * 100)}%" for v in (value.red, value.green, value.blue)) + ")"
    )


def style_attributes(style: Style, gradient_id: str | None = None) -> str:
    fill = (
        f"url(#{gradient_id})"
        if gradient_id is not None
        else color(style.fill if isinstance(style.fill, Color) else None)
    )
    return (
        f'fill="{fill}" stroke="{color(style.stroke)}" opacity="{number(style.opacity)}" '
        f'stroke-width="{number(style.line_width)}" '
        f'stroke-linecap="{style.line_cap}" stroke-linejoin="{style.line_join}" '
        f'stroke-miterlimit="10" fill-rule="{style.fill_rule}"'
    )


def path_data(geometry: PathSource) -> str:
    parts: list[str] = []
    for command in geometry.to_path().commands:
        match command:
            case Move(end):
                parts.append(f"M {number(end.x)} {number(end.y)}")
            case Segment(end):
                parts.append(f"L {number(end.x)} {number(end.y)}")
            case Quadratic(control, end):
                parts.append(
                    f"Q {number(control.x)} {number(control.y)} {number(end.x)} {number(end.y)}"
                )
            case Cubic(c1, c2, end):
                parts.append(
                    f"C {number(c1.x)} {number(c1.y)} "
                    f"{number(c2.x)} {number(c2.y)} "
                    f"{number(end.x)} {number(end.y)}"
                )
            case Close():
                parts.append("Z")
    return " ".join(parts)


def shape(geometry: Geometry) -> str:
    """Encode supported native geometry, falling back to optional path conversion."""
    if isinstance(geometry, Circle):
        p = point(geometry.center)
        return f'circle cx="{number(p.x)}" cy="{number(p.y)}" r="{number(geometry.radius)}"'
    if isinstance(geometry, Rectangle):
        p = point(geometry.origin)
        return (
            f'rect x="{number(p.x)}" y="{number(p.y)}" '
            f'width="{number(geometry.width)}" height="{number(geometry.height)}"'
        )
    if isinstance(geometry, Arc):
        p = geometry.at(geometry.start_angle)
        data = f"M {number(p.x)} {number(p.y)}"
        # Split full circles as coincident SVG arc endpoints omit the arc.

        count = max(1, ceil(abs(geometry.sweep_angle) / 180))
        for i in range(count):
            end = geometry.at(geometry.start_angle + geometry.sweep_angle * (i + 1) / count)
            data += (
                f" A {number(geometry.radius_x)} {number(geometry.radius_y)} "
                f"{number(geometry.rotation)} 0 {int(geometry.sweep_angle > 0)} "
                f"{number(end.x)} {number(end.y)}"
            )
        return f'path d="{data}"'
    if isinstance(geometry, PathSource):
        return f'path d="{path_data(geometry)}"'
    raise TypeError(f"Unsupported render geometry: {type(geometry).__name__}.")
