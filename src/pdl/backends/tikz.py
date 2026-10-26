"""TikZ output with native shapes and generic path lowering."""

from pdl.backends._format import number
from pdl.canvas import Canvas, Color
from pdl.geometry import (
    Arc,
    Circle,
    Close,
    Cubic,
    Geometry,
    Move,
    Point,
    Quadratic,
    Rectangle,
    Segment,
    point,
)


def coordinate(p: Point) -> str:
    return f"({number(p.x)},{number(p.y)})"


def color(value: Color) -> str:
    return (
        "{rgb,1:red,"
        + number(value.red)
        + ";green,"
        + number(value.green)
        + ";blue,"
        + number(value.blue)
        + "}"
    )


def path_data(geometry: Geometry) -> str:
    if isinstance(geometry, Circle):
        return f"{coordinate(point(geometry.center))} circle[radius={number(geometry.radius)}mm]"
    if isinstance(geometry, Rectangle):
        p = point(geometry.origin)
        return (
            f"{coordinate(p)} rectangle "
            f"{coordinate(Point(p.x + geometry.width, p.y + geometry.height))}"
        )
    if isinstance(geometry, Arc) and geometry.rotation == 0:
        return (
            f"{coordinate(geometry.at(geometry.start_angle))} arc["
            f"start angle={number(geometry.start_angle)},"
            f"delta angle={number(geometry.sweep_angle)},"
            f"x radius={number(geometry.radius_x)}mm,"
            f"y radius={number(geometry.radius_y)}mm]"
        )
    parts: list[str] = []
    current = Point(0, 0)
    start = current
    for command in geometry.to_path().commands:
        match command:
            case Move(end):
                parts.append(coordinate(end))
                start = current = end
            case Segment(end):
                parts.append(f"-- {coordinate(end)}")
                current = end
            case Quadratic(control, end):
                c1 = Point(
                    current.x + 2 / 3 * (control.x - current.x),
                    current.y + 2 / 3 * (control.y - current.y),
                )
                c2 = Point(
                    end.x + 2 / 3 * (control.x - end.x),
                    end.y + 2 / 3 * (control.y - end.y),
                )
                parts.append(
                    f".. controls {coordinate(c1)} and {coordinate(c2)} .. {coordinate(end)}"
                )
                current = end
            case Cubic(c1, c2, end):
                parts.append(
                    f".. controls {coordinate(c1)} and {coordinate(c2)} .. {coordinate(end)}"
                )
                current = end
            case Close():
                parts.append("-- cycle")
                current = start
    return " ".join(parts)


def render(canvas: Canvas) -> str:
    w, h = number(canvas.width), number(canvas.height)
    lines = [
        r"\documentclass[tikz,border=0pt]{standalone}",
        r"\begin{document}",
        r"\begin{tikzpicture}[x=1mm,y=1mm]",
        f"\\path[use as bounding box] (0,0) rectangle ({w},{h});",
        f"\\clip (0,0) rectangle ({w},{h});",
    ]
    for drawing in canvas.drawings:
        s = drawing.style
        # PGF zero-width strokes are hairlines; suppress them for SVG parity.
        stroke = s.stroke if s.line_width > 0 else None
        options = [
            f"draw={color(stroke) if stroke is not None else 'none'}",
            f"fill={color(s.fill) if s.fill is not None else 'none'}",
            f"line width={number(s.line_width)}mm",
            f"line cap={s.line_cap}",
            f"line join={s.line_join}",
            "miter limit=10",
            "even odd rule" if s.fill_rule == "evenodd" else "nonzero rule",
        ]
        lines.append("\\path[" + ",".join(options) + "] " + path_data(drawing.geometry) + ";")
    lines.extend([r"\end{tikzpicture}", r"\end{document}"])
    return "\n".join(lines) + "\n"
