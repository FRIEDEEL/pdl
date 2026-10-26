"""Ordered drawing container and backend-independent paint."""

from contextlib import AbstractContextManager
from math import isfinite
from pathlib import Path as FilePath
from typing import Literal

from pdl.bounds import Anchor, Bounds
from pdl.geometry import Point
from pdl.paint import BLACK as BLACK
from pdl.paint import Color as Color
from pdl.paint import Style as Style
from pdl.renderer import RendererConfig, rendering
from pdl.scene import Drawing, Graphic
from pdl.scene import bounds as scene_bounds
from pdl.text import Font


class Canvas:
    """A fixed Cartesian viewport measured in millimeters.

    The origin is the bottom-left corner. Drawings are rendered in insertion
    order; later drawings cover earlier ones. Geometry is read at export time.
    Content outside the viewport is clipped.
    """

    def __init__(
        self,
        width: float,
        height: float,
        *,
        fonts: tuple[Font, ...] = (),
        renderer: RendererConfig | None = None,
    ) -> None:
        if not all(isfinite(v) and v > 0 for v in (width, height)):
            raise ValueError("Canvas dimensions must be positive and finite.")
        self.width = width
        self.height = height
        self.renderer = renderer or RendererConfig(fonts=fonts)
        self._drawings: list[Drawing] = []

    @property
    def drawings(self) -> tuple[Drawing, ...]:
        return tuple(self._drawings)

    def draw(self, geometry: Graphic, style: Style | None = None) -> None:
        """Append geometry and paint; do not flatten the geometry."""
        self._drawings.append(Drawing(geometry, style))

    def typography(self, fonts: tuple[Font, ...] | None = None) -> AbstractContextManager[None]:
        """Share the canvas font policy with authoring-time measurements."""
        return rendering(
            self.renderer if fonts is None else RendererConfig(fonts=fonts, tex=self.renderer.tex)
        )

    def bounds(self, graphic: Graphic) -> Bounds:
        """Measure geometry or layout using this canvas's font policy."""
        with self.typography():
            return scene_bounds(graphic)

    def anchor(self, graphic: Graphic, name: Anchor = "center") -> Point:
        """Measure an explicit anchor using the same policy as export."""
        from pdl.nodes import Node

        with self.typography():
            if isinstance(graphic, Node):
                return graphic.anchor(name)
            return scene_bounds(graphic).anchor(name)

    def render(
        self,
        backend: Literal["svg", "tikz"] = "svg",
        *,
        standalone: bool = True,
        fonts: tuple[Font, ...] | None = None,
        renderer: RendererConfig | None = None,
    ) -> str:
        """Export with optional ordered defaults for Text without an explicit font.

        For content-sized nodes and anchor snapshots, configure fonts on the
        canvas before measuring; changing fonts at export does not reroute
        previously constructed connections.
        """
        from pdl.backends.svg import render as svg_render
        from pdl.backends.tikz import render as tikz_render

        context = rendering(renderer) if renderer is not None else self.typography(fonts)
        with context:
            if backend == "svg":
                return svg_render(self)
            if backend == "tikz":
                return tikz_render(self, standalone=standalone)
            raise ValueError(f"Unknown backend: {backend}")

    def latex_preamble(self) -> str:
        """Return required packages and macros for an embedded TikZ fragment."""
        from pdl.backends.tikz_text import preamble

        with self.typography():
            return preamble(self)

    def save(
        self,
        filename: str | FilePath,
        *,
        backend: Literal["svg", "tikz"],
        fonts: tuple[Font, ...] | None = None,
    ) -> None:
        """Write the selected output as UTF-8 text."""
        FilePath(filename).write_text(self.render(backend, fonts=fonts), encoding="utf-8")
