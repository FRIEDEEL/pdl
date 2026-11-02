"""Reusable example components."""

from examples._shared.config import BLUE, INK
from pdl import Color, Group, Line, Polygon, Style
from pdl.author.entity.factories import as_entity


def valve() -> Group:
    """Define a reusable local-coordinate valve symbol."""
    body = Polygon(((-5, -3), (5, 3), (5, -3), (-5, 3)))
    stem = Line((0, 0), (0, 6))
    handle = Line((-3, 6), (3, 6))
    return Group(
        as_entity(body, Style(stroke=BLUE, fill=Color(1, 1, 1), line_width=0.45)),
        as_entity(stem, INK),
        as_entity(handle, INK),
    )
