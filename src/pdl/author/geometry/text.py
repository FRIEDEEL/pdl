"""Editable literal text backed by shared font measurement."""

from __future__ import annotations

from dataclasses import dataclass, field
from math import isfinite
from pathlib import Path as FilePath
from typing import Literal

from pdl.author.geometry.bounds import Bounds, geometry_bounds
from pdl.author.geometry.path import Path
from pdl.author.geometry.point import Position
from pdl.author.geometry.point import as_point as point
from pdl.author.geometry.typography import (
    FontKey,
    TextLayout,
    measure_text,
)
from pdl.author.style.font import Font, FontStack
from pdl.author.style.font_policy import font_policy
from pdl.author.style.typography import default_fonts
from pdl.author.transform.affine import Rotation, Translation


@dataclass(eq=False)
class Text:
    """Literal Unicode text at a first-line baseline reference.

    Args:
        text: Literal content; newline begins an explicit new line. No automatic wrapping.
        font: Explicit Font or FontStack. ``None`` uses renderer defaults.
        position: First baseline reference in local millimeters, not a bounds center.
        size: Positive font size in TeX points (1/72.27 inch).
        align: Each line's alignment about the reference: left, center, or right.
        line_spacing: Positive baseline distance as a multiple of font size.

    Text does not interpret LaTeX syntax. Native Text paint must be fill-only;
    when passing a Style, set ``stroke=None``. Without an explicit style, text
    uses black fill. SVG references installed fonts; native TikZ uses LaTeX.
    Their rendering and metrics can differ slightly.

    Direct layout access needs explicit fonts or an active canvas typography
    context. Canvas rendering establishes that context and discovers default
    fonts when needed.

    Raises:
        ValueError: Size, line spacing, alignment, or coordinates are invalid.
    """

    text: str
    font: Font | FontStack | None = None
    position: Position = (0, 0)
    size: float = 12
    align: Literal["left", "center", "right"] = "left"
    line_spacing: float = 1.25

    rotation: float = 0

    _measurement: TextLayout | None = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        point(self.position)
        if not isfinite(self.rotation):
            raise ValueError("Text rotation must be finite.")
        if not all(isfinite(v) and v > 0 for v in (self.size, self.line_spacing)):
            raise ValueError("Font size and line spacing must be finite and positive.")
        if self.align not in ("left", "center", "right"):
            raise ValueError("Unknown text alignment.")

    @property
    def layout(self) -> TextLayout:
        if self._measurement is not None:
            return self._measurement
        selected = (
            self.font.fonts
            if isinstance(self.font, FontStack)
            else (self.font,)
            if isinstance(self.font, Font)
            else font_policy.get()
        )
        if callable(selected):
            selected = selected()
        if not selected:
            selected = default_fonts()
        files: list[FontKey] = []
        for font in selected:
            file = FilePath(font.file).resolve()
            stat = file.stat()
            files.append((str(file), font.index, stat.st_mtime_ns, stat.st_size))
        return measure_text(tuple(files), self.text, self.size, self.align, self.line_spacing)

    def capture_layout(self) -> None:
        """Fix measured layout on a captured description before output."""
        self._measurement = self.layout

    @property
    def layout_bounds(self) -> Bounds:
        p = point(self.position)
        return self.layout.box.transformed(Translation(p.x, p.y) @ Rotation(self.rotation))

    @property
    def ink_bounds(self) -> Bounds:
        return geometry_bounds(self.to_path())

    def to_path(self) -> Path:
        p = point(self.position)
        return self.layout.to_path().mapped(Translation(p.x, p.y) @ Rotation(self.rotation))
