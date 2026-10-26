"""Explicit-font text shaping, measurement and vector outline fallback."""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from math import isfinite
from pathlib import Path as FilePath
from typing import Literal

import uharfbuzz as hb

from pdl.bounds import Bounds, geometry_bounds
from pdl.fonts import glyph_path
from pdl.geometry import Path, Position, point
from pdl.transforms import Transform, transform_path

# Use TeX points consistently for both ordinary text and TeX fragments.
PT_TO_MM = 25.4 / 72.27


@dataclass(frozen=True)
class Font:
    """An explicit static TTF/OTF font, optionally indexed within a collection."""

    file: str | FilePath
    index: int = 0

    def __post_init__(self) -> None:
        if self.index < 0:
            raise ValueError("Font index must be nonnegative.")
        if not FilePath(self.file).is_file():
            raise FileNotFoundError(self.file)


@dataclass(frozen=True)
class TextLayout:
    """Layout metrics relative to the first baseline, in millimeters."""

    box: Bounds
    ink: Bounds
    advances: tuple[float, ...]
    _outline: Path

    def to_path(self) -> Path:
        return self._outline.to_path()


def _append(target: Path, source: Path) -> None:
    # Concatenation preserves independent contours and their winding direction.
    from pdl.geometry import Close, Cubic, Move, Quadratic, Segment

    for command in source.commands:
        match command:
            case Move(end):
                target.move_to(end)
            case Segment(end):
                target.line_to(end)
            case Quadratic(control, end):
                target.quadratic_to(control, end)
            case Cubic(c1, c2, end):
                target.cubic_to(c1, c2, end)
            case Close():
                target.close()


@lru_cache(maxsize=128)
def _layout(
    file: str,
    index: int,
    stamp: tuple[int, int],
    text: str,
    size: float,
    align: str,
    line_spacing: float,
) -> TextLayout:
    del stamp  # The stat signature invalidates cached layouts after font edits.
    data = FilePath(file).read_bytes()
    face = hb.Face(data, index)
    font = hb.Font(face)
    font.scale = (face.upem, face.upem)
    scale = size * PT_TO_MM / face.upem
    extents = font.get_font_extents("ltr")
    ascender, descender = extents.ascender * scale, extents.descender * scale
    path = Path()
    widths: list[float] = []
    lines = text.split("\n")
    for row, content in enumerate(lines):
        buffer = hb.Buffer()
        buffer.add_str(content)
        buffer.guess_segment_properties()
        hb.shape(font, buffer)
        infos, positions = buffer.glyph_infos, buffer.glyph_positions
        if any(info.codepoint == 0 for info in infos):
            raise ValueError(f"Font {file!r} lacks glyphs needed for {content!r}.")
        width = sum(p.x_advance for p in positions) * scale
        widths.append(width)
        offset = -width / 2 if align == "center" else -width if align == "right" else 0
        x, y = offset, -row * size * PT_TO_MM * line_spacing
        for info, position in zip(infos, positions, strict=True):
            outline = glyph_path(file, index, info.codepoint)
            placement = Transform.translate(
                x + position.x_offset * scale, y + position.y_offset * scale
            ) @ Transform.scale(scale)
            _append(path, transform_path(outline, placement))
            x += position.x_advance * scale
            y += position.y_advance * scale
    width = max(widths, default=0)
    left = -width / 2 if align == "center" else -width if align == "right" else 0
    box = Bounds(
        left, descender - (len(lines) - 1) * size * PT_TO_MM * line_spacing, left + width, ascender
    )
    return TextLayout(box, geometry_bounds(path), tuple(widths), path)


@dataclass(frozen=True)
class Text:
    """Literal horizontal text at a first-line baseline position.

    Args:
        text: Literal Unicode content; newline starts an explicit new line.
        font: An explicit font file, with no automatic fallback.
        position: First baseline reference point in millimeters.
        size: Font size in TeX points (1/72.27 inch).
        align: Alignment of every line around the baseline reference.
        line_spacing: Baseline distance as a multiple of font size.
    """

    text: str
    font: Font
    position: Position = (0, 0)
    size: float = 12
    align: Literal["left", "center", "right"] = "left"
    line_spacing: float = 1.25

    def __post_init__(self) -> None:
        point(self.position)
        if not all(isfinite(v) and v > 0 for v in (self.size, self.line_spacing)):
            raise ValueError("Font size and line spacing must be finite and positive.")
        if self.align not in ("left", "center", "right"):
            raise ValueError("Unknown text alignment.")

    @property
    def layout(self) -> TextLayout:
        file = FilePath(self.font.file).resolve()
        stat = file.stat()
        return _layout(
            str(file),
            self.font.index,
            (stat.st_mtime_ns, stat.st_size),
            self.text,
            self.size,
            self.align,
            self.line_spacing,
        )

    @property
    def layout_bounds(self) -> Bounds:
        p = point(self.position)
        return self.layout.box.transformed(Transform.translate(p.x, p.y))

    @property
    def ink_bounds(self) -> Bounds:
        return geometry_bounds(self.to_path())

    def to_path(self) -> Path:
        p = point(self.position)
        return transform_path(self.layout.to_path(), Transform.translate(p.x, p.y))
