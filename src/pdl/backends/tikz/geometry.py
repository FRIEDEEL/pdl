"""TikZ output with native shapes and generic path lowering."""

from pdl.author.geometry.base import Geometry
from pdl.author.geometry.path import (
    Close,
    Cubic,
    Move,
    Point,
    Quadratic,
    Segment,
)
from pdl.author.geometry.point import as_point as point
from pdl.author.geometry.protocols import PathSource
from pdl.author.geometry.shapes import Arc, Circle, Rectangle
from pdl.author.style import Color, Style
from pdl.backends.formatting import number


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


def paint_options(style: Style) -> list[str]:
    stroke = style.stroke if style.line_width > 0 else None
    return [
        f"draw={color(stroke) if stroke is not None else 'none'}",
        f"fill={color(style.fill) if isinstance(style.fill, Color) else 'none'}",
        f"draw opacity={number(style.opacity)}",
        f"fill opacity={number(style.opacity)}",
        f"line width={number(style.line_width)}mm",
        f"line cap={style.line_cap}",
        f"line join={style.line_join}",
        "miter limit=10",
        "even odd rule" if style.fill_rule == "evenodd" else "nonzero rule",
    ]


def path_data(geometry: Geometry) -> str:
    """Encode supported native geometry, falling back to optional path conversion."""
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
    if not isinstance(geometry, PathSource):
        raise TypeError(f"Unsupported render geometry: {type(geometry).__name__}.")
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
