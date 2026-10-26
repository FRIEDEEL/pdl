"""Optional geometry/layout overlays for example inspection."""

from pdl.geometry import Circle, Line, Rectangle, point
from pdl.paint import Color, Style
from pdl.scene import Drawing, Graphic, Group, bounds, walk
from pdl.tex import TeX
from pdl.text import PT_TO_MM, Text


def debug_overlay(graphic: Graphic) -> Group:
    """Show an object's bounds, rectangular anchors and text baselines.

    Return only the overlay, so callers can draw the original object first.
    Text boxes are layout bounds, not ink bounds. Stroke expansion is excluded.
    """
    box = bounds(graphic)
    red = Style(stroke=Color(0.8, 0.2, 0.25), line_width=0.15)
    green = Style(stroke=Color(0.1, 0.6, 0.4), line_width=0.15)
    children = [Drawing(Rectangle((box.left, box.bottom), box.width, box.height), red)]
    for name in ("center", "north", "south", "east", "west"):
        children.append(Drawing(Circle(box.anchor(name), 0.35), red))
    for drawing in walk((Drawing(graphic),)):
        text = drawing.geometry
        if isinstance(text, (Text, TeX)):
            layout = text.layout_bounds
            children.append(
                Drawing(
                    Rectangle((layout.left, layout.bottom), layout.width, layout.height),
                    green,
                    drawing.transform,
                )
            )
            p = point(text.position)
            rows = len(text.text.split("\n")) if isinstance(text, Text) else 1
            for row in range(rows):
                y = p.y - row * text.size * PT_TO_MM * (
                    text.line_spacing if isinstance(text, Text) else 1
                )
                children.append(
                    Drawing(
                        Line((layout.left - 1, y), (layout.right + 1, y)), green, drawing.transform
                    )
                )
    return Group(tuple(children))
