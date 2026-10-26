"""SVG output with native shapes and path fallback."""

from pdl.backends._format import number
from pdl.canvas import Canvas, Color, Style
from pdl.geometry import (
    Arc,
    Circle,
    Close,
    Cubic,
    Geometry,
    Move,
    Quadratic,
    Rectangle,
    Segment,
    point,
)


def color(value: Color | None) -> str:
    if value is None:
        return "none"
    return (
        "rgb(" + ",".join(f"{number(v * 100)}%" for v in (value.red, value.green, value.blue)) + ")"
    )


def style_attributes(style: Style) -> str:
    return (
        f'fill="{color(style.fill)}" stroke="{color(style.stroke)}" '
        f'stroke-width="{number(style.line_width)}" '
        f'stroke-linecap="{style.line_cap}" stroke-linejoin="{style.line_join}" '
        f'stroke-miterlimit="10" fill-rule="{style.fill_rule}"'
    )


def path_data(geometry: Geometry) -> str:
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
        from math import ceil

        count = max(1, ceil(abs(geometry.sweep_angle) / 180))
        for i in range(count):
            end = geometry.at(geometry.start_angle + geometry.sweep_angle * (i + 1) / count)
            data += (
                f" A {number(geometry.radius_x)} {number(geometry.radius_y)} "
                f"{number(geometry.rotation)} 0 {int(geometry.sweep_angle > 0)} "
                f"{number(end.x)} {number(end.y)}"
            )
        return f'path d="{data}"'
    return f'path d="{path_data(geometry)}"'


def render(canvas: Canvas) -> str:
    w, h = number(canvas.width), number(canvas.height)
    elements = [f"  <{shape(d.geometry)} {style_attributes(d.style)}/>" for d in canvas.drawings]
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}mm" height="{h}mm" '
        f'viewBox="0 0 {w} {h}" overflow="hidden">\n'
        f'<g transform="translate(0 {h}) scale(1 -1)">\n' + "\n".join(elements) + "\n</g>\n</svg>\n"
    )
