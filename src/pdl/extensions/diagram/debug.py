"""Explicit geometry/layout overlays for inspecting drawings and examples."""

from dataclasses import dataclass

from pdl.author.entity.base import Entity
from pdl.author.entity.capture import Composite, freeze, walk
from pdl.author.entity.factories import circle, line, rectangle
from pdl.author.geometry.point import as_point
from pdl.author.geometry.tex import TeX
from pdl.author.geometry.text import Text
from pdl.author.geometry.typography import PT_TO_MM
from pdl.author.style import Color, Style


@dataclass(frozen=True)
class DebugOverlay:
    graphic: Entity | Composite

    def decompose(self) -> tuple[Entity, ...]:
        graphic = freeze(self.graphic)
        box = graphic.bounds
        if box.is_empty:
            return ()
        red = Style(stroke=Color(0.8, 0.2, 0.25), line_width=0.15)
        green = Style(stroke=Color(0.1, 0.6, 0.4), line_width=0.15)
        children = [rectangle((box.left, box.bottom), box.width, box.height, style=red)]
        for name in ("center", "north", "south", "east", "west"):
            children.append(circle(box.anchor(name), 0.35, style=red))
        for drawing in walk((graphic,)):
            text = drawing.geometry
            if not isinstance(text, (Text, TeX)):
                continue
            layout = text.layout_bounds
            children.append(
                rectangle((layout.left, layout.bottom), layout.width, layout.height, style=green)
            )
            p = as_point(text.position)
            rows = len(text.text.split("\n")) if isinstance(text, Text) else 1
            for row in range(rows):
                y = p.y - row * text.size * PT_TO_MM * (
                    text.line_spacing if isinstance(text, Text) else 1
                )
                children.append(line((layout.left - 1, y), (layout.right + 1, y), style=green))
        return tuple(children)


def debug_overlay(graphic: Entity | Composite) -> DebugOverlay:
    """Return only the overlay; submit the source separately when desired."""
    return DebugOverlay(graphic)
