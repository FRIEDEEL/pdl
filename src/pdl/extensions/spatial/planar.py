"""Explicit vector-path lowering for perspective plane artwork."""

from __future__ import annotations

from dataclasses import dataclass
from math import hypot
from typing import TYPE_CHECKING

from pdl.author.entity.base import Entity
from pdl.author.entity.capture import Composite, walk
from pdl.author.geometry.image import Image
from pdl.author.geometry.path import Close, Cubic, Move, Path, Quadratic, Segment
from pdl.author.geometry.point import Point
from pdl.author.geometry.protocols import PathSource
from pdl.author.geometry.tex import TeX
from pdl.author.geometry.text import Text
from pdl.author.style import BLACK, Color, Style
from pdl.extensions.spatial._author import make_entity
from pdl.extensions.spatial.solids import Plane3D

if TYPE_CHECKING:
    from pdl.extensions.spatial.projection import PerspectiveCamera


@dataclass(frozen=True)
class PerspectiveArtwork:
    """Captured plane content lowered in the eventual Canvas font context.

    Lines project exactly. Curves and glyph contours become polylines with
    projected control-hull deviation at most 0.02 local output millimeters.
    Outer 2D scaling scales this tolerance too. Strokes remain constant-width
    Canvas strokes, not perspective-transformed ink ribbons. Solid fills only;
    images and gradients are unsupported. All curve controls must be beyond
    the camera near plane, a conservative restriction without clipping.
    """

    plane: Plane3D
    drawing: Entity
    camera: PerspectiveCamera

    def decompose(self) -> tuple[Entity, ...]:
        result: list[Entity] = []
        for leaf in walk((self.drawing,)):
            geometry = leaf.geometry
            if isinstance(geometry, Composite):
                raise TypeError("Expected a path-compatible leaf after composite traversal.")
            if isinstance(geometry, Image):
                raise ValueError("Perspective artwork does not support embedded images.")
            style = leaf.effective_style
            if isinstance(geometry, (Text, TeX)):
                style = style or Style(stroke=None, fill=BLACK)
                if style.stroke is not None:
                    raise ValueError("Perspective text requires fill-only paint (stroke=None).")
            style = style or Style()
            if style.fill is not None and not isinstance(style.fill, Color):
                raise ValueError("Perspective artwork currently supports solid fills only.")
            if not isinstance(geometry, PathSource):
                raise TypeError("Expected path-compatible plane artwork.")
            path = Path()

            def project(p: Point) -> Point:
                local = p
                return self.camera.project(self.plane.point(local.x, local.y))

            def curve(controls: tuple[Point, ...], level: int = 0) -> None:
                projected = tuple(project(p) for p in controls)
                a, b = projected[0], projected[-1]
                dx, dy = b.x - a.x, b.y - a.y
                length_squared = dx * dx + dy * dy

                def deviation(p: Point) -> float:
                    t = (
                        0.0
                        if length_squared == 0
                        else max(
                            0.0, min(1.0, ((p.x - a.x) * dx + (p.y - a.y) * dy) / length_squared)
                        )
                    )
                    return hypot(p.x - a.x - t * dx, p.y - a.y - t * dy)

                if max(deviation(p) for p in projected) <= 0.02:
                    path.line_to(b)
                    return
                if level >= 24:
                    raise ValueError("Perspective curve subdivision exceeded its safety limit.")
                rows = [controls]
                while len(rows[-1]) > 1:
                    row = rows[-1]
                    rows.append(
                        tuple(Point((a.x + b.x) / 2, (a.y + b.y) / 2) for a, b in zip(row, row[1:]))
                    )
                curve(tuple(row[0] for row in rows), level + 1)
                curve(tuple(row[-1] for row in reversed(rows)), level + 1)

            current = Point(0, 0)
            start = current
            for command in geometry.to_path().commands:
                match command:
                    case Move(end):
                        path.move_to(project(end))
                        current = start = end
                    case Segment(end):
                        path.line_to(project(end))
                        current = end
                    case Quadratic(control, end):
                        curve((current, control, end))
                        current = end
                    case Cubic(c1, c2, end):
                        curve((current, c1, c2, end))
                        current = end
                    case Close():
                        path.close()
                        current = start
            result.append(make_entity(path, style))
        return tuple(result)
