"""Ordered drawing container and backend-independent paint."""

from dataclasses import dataclass
from math import isfinite
from pathlib import Path as FilePath
from typing import Literal

from pdl.geometry import Geometry


@dataclass(frozen=True)
class Color:
    """An RGB color with channels in the inclusive range zero to one."""

    red: float
    green: float
    blue: float

    def __post_init__(self) -> None:
        if not all(isfinite(v) and 0 <= v <= 1 for v in (self.red, self.green, self.blue)):
            raise ValueError("Color channels must be between zero and one.")


BLACK = Color(0, 0, 0)


@dataclass(frozen=True)
class Style:
    """Explicit fill and stroke properties, with no backend defaults."""

    stroke: Color | None = BLACK
    fill: Color | None = None
    line_width: float = 1
    line_cap: Literal["butt", "round", "square"] = "butt"
    line_join: Literal["miter", "round", "bevel"] = "miter"
    fill_rule: Literal["nonzero", "evenodd"] = "nonzero"

    def __post_init__(self) -> None:
        if not isfinite(self.line_width) or self.line_width < 0:
            raise ValueError("Line width must be finite and nonnegative.")
        if self.line_cap not in ("butt", "round", "square"):
            raise ValueError("Unknown line cap.")
        if self.line_join not in ("miter", "round", "bevel"):
            raise ValueError("Unknown line join.")
        if self.fill_rule not in ("nonzero", "evenodd"):
            raise ValueError("Unknown fill rule.")


@dataclass(frozen=True)
class Drawing:
    geometry: Geometry
    style: Style


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

    def draw(self, geometry: Geometry, style: Style | None = None) -> None:
        """Append geometry and paint; do not flatten the geometry."""
        self._drawings.append(Drawing(geometry, style if style is not None else Style()))

    def render(self, backend: Literal["svg", "tikz"] = "svg") -> str:
        """Return SVG markup or a standalone compilable TikZ document."""
        from pdl.backends.svg import render as svg_render
        from pdl.backends.tikz import render as tikz_render

        if backend == "svg":
            return svg_render(self)
        if backend == "tikz":
            return tikz_render(self)
        raise ValueError(f"Unknown backend: {backend}")

    def save(self, filename: str | FilePath, *, backend: Literal["svg", "tikz"]) -> None:
        """Write the selected output as UTF-8 text."""
        FilePath(filename).write_text(self.render(backend), encoding="utf-8")
