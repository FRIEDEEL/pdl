"""Ordered drawing container and backend-independent paint."""

from contextlib import AbstractContextManager
from math import isfinite
from pathlib import Path as FilePath
from typing import Literal

from pdl.geometry.bounds import Bounds
from pdl.rendering.config import RendererConfig, rendering
from pdl.scene.composition import Drawing, Graphic
from pdl.scene.composition import bounds as scene_bounds
from pdl.scene.paint import BLACK as BLACK
from pdl.scene.paint import Color as Color
from pdl.scene.paint import Style as Style
from pdl.typography.plain import Font


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

    def draw(self, geometry: Graphic | Drawing, style: Style | None = None) -> None:
        """Append geometry and paint; do not flatten the geometry."""
        if isinstance(geometry, Drawing):
            if style is not None:
                geometry = Drawing(geometry.geometry, style, geometry.transform)
            self._drawings.append(geometry)
        else:
            self._drawings.append(Drawing(geometry, style))

    def typography(self, fonts: tuple[Font, ...] | None = None) -> AbstractContextManager[None]:
        """Use the canvas policy for explicitly requested measurements."""
        return rendering(
            self.renderer if fonts is None else RendererConfig(fonts=fonts, tex=self.renderer.tex)
        )

    def bounds(self, graphic: Graphic | Drawing) -> Bounds:
        """Measure geometry or layout using this canvas's font policy."""
        with self.typography():
            return scene_bounds(graphic)

    def render(
        self,
        backend: Literal["svg", "tikz"] = "svg",
        *,
        standalone: bool = True,
        fonts: tuple[Font, ...] | None = None,
        renderer: RendererConfig | None = None,
    ) -> str:
        """Export with optional ordered defaults for Text without an explicit font.

        Content sizes and anchor references are evaluated for this invocation.
        Changing export fonts also recomputes dependent connection endpoints.
        """
        from pdl.rendering.svg.document import render as svg_render
        from pdl.rendering.tikz.document import render as tikz_render

        context = rendering(renderer) if renderer is not None else self.typography(fonts)
        with context:
            if backend == "svg":
                return svg_render(self)
            if backend == "tikz":
                return tikz_render(self, standalone=standalone)
            raise ValueError(f"Unknown backend: {backend}")

    def latex_preamble(self) -> str:
        """Return required packages and macros for an embedded TikZ fragment."""
        from pdl.rendering.tikz.nodes import supports
        from pdl.rendering.tikz.text import preamble
        from pdl.rendering.traversal import prepare

        with self.typography():
            return preamble(tuple(prepare(self.drawings, supports)))

    def save(
        self,
        filename: str | FilePath,
        *,
        backend: Literal["svg", "tikz"],
        fonts: tuple[Font, ...] | None = None,
    ) -> None:
        """Write the selected output as UTF-8 text."""
        FilePath(filename).write_text(self.render(backend, fonts=fonts), encoding="utf-8")
