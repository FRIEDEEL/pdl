"""Ordered drawing container and backend-independent paint."""

from math import isfinite
from pathlib import Path as FilePath
from typing import Literal

from pdl.paint import BLACK as BLACK
from pdl.paint import Color as Color
from pdl.paint import Style as Style
from pdl.scene import Drawing, Graphic


class Canvas:
    """A fixed Cartesian viewport measured in millimeters.

    The origin is the bottom-left corner. Drawings are rendered in insertion
    order; later drawings cover earlier ones. Geometry is read at export time.
    Content outside the viewport is clipped.
    """

    def __init__(self, width: float, height: float) -> None:
        if not all(isfinite(v) and v > 0 for v in (width, height)):
            raise ValueError("Canvas dimensions must be positive and finite.")
        self.width = width
        self.height = height
        self._drawings: list[Drawing] = []

    @property
    def drawings(self) -> tuple[Drawing, ...]:
        return tuple(self._drawings)

    def draw(self, geometry: Graphic, style: Style | None = None) -> None:
        """Append geometry and paint; do not flatten the geometry."""
        self._drawings.append(Drawing(geometry, style))

    def render(self, backend: Literal["svg", "tikz"] = "svg", *, standalone: bool = True) -> str:
        """Return SVG markup or a standalone compilable TikZ document."""
        from pdl.backends.svg import render as svg_render
        from pdl.backends.tikz import render as tikz_render

        if backend == "svg":
            return svg_render(self)
        if backend == "tikz":
            return tikz_render(self, standalone=standalone)
        raise ValueError(f"Unknown backend: {backend}")

    def latex_preamble(self) -> str:
        """Return required packages and macros for an embedded TikZ fragment."""
        from pdl.backends.tikz_text import preamble

        return preamble(self)

    def save(self, filename: str | FilePath, *, backend: Literal["svg", "tikz"]) -> None:
        """Write the selected output as UTF-8 text."""
        FilePath(filename).write_text(self.render(backend), encoding="utf-8")
