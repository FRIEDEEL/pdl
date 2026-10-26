"""Explicit-font text shaping, measurement and vector outline fallback."""

from __future__ import annotations

import unicodedata
from collections.abc import Generator
from contextlib import contextmanager
from contextvars import ContextVar
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
class FontStack:
    """An ordered font candidate list, searched per combining sequence."""

    fonts: tuple[Font, ...]

    def __post_init__(self) -> None:
        if not self.fonts:
            raise ValueError("A FontStack needs at least one font.")


_font_context: ContextVar[tuple[Font, ...]] = ContextVar("pdl_fonts", default=())


@contextmanager
def font_context(fonts: tuple[Font, ...]) -> Generator[None, None, None]:
    """Use task-local defaults for measurement and rendering together."""
    token = _font_context.set(fonts)
    try:
        yield
    finally:
        _font_context.reset(token)


@dataclass(frozen=True)
class TextLayout:
    """Layout metrics relative to the first baseline, in millimeters."""

    box: Bounds
    ink: Bounds
    advances: tuple[float, ...]
    fonts_used: tuple[str, ...]
    _outline: Path

    def to_path(self) -> Path:
        return self._outline.to_path()


def _clusters(text: str) -> list[str]:
    """Keep combining marks, variation selectors and joiner sequences together.

    This is a horizontal-label subset, not a complete Unicode grapheme or
    bidirectional paragraph implementation.
    """
    result: list[str] = []
    for character in text:
        attached = (
            unicodedata.category(character).startswith("M")
            or character == "\u200d"
            or (result and result[-1].endswith("\u200d"))
        )
        if result and attached:
            result[-1] += character
        else:
            result.append(character)
    return result


def _shape(font: hb.Font, text: str) -> tuple[list[hb.GlyphInfo], list[hb.GlyphPosition]]:
    buffer = hb.Buffer()
    buffer.add_str(text)
    buffer.guess_segment_properties()
    hb.shape(font, buffer)
    return buffer.glyph_infos, buffer.glyph_positions


type FontKey = tuple[str, int, int, int]


@lru_cache(maxsize=128)
def _layout(
    files: tuple[FontKey, ...], text: str, size: float, align: str, line_spacing: float
) -> TextLayout:
    if any(unicodedata.bidirectional(c) in ("R", "AL", "AN") for c in text):
        raise ValueError(
            "Stage 2 Text supports left-to-right labels; use TeX for complex directionality."
        )
    fonts: list[hb.Font] = []
    scales: list[float] = []
    for file, index, _, _ in files:
        face = hb.Face(FilePath(file).read_bytes(), index)
        font = hb.Font(face)
        font.scale = (face.upem, face.upem)
        fonts.append(font)
        scales.append(size * PT_TO_MM / face.upem)
    path = Path()
    widths: list[float] = []
    used: set[int] = set()
    lines = text.split("\n")
    for row, content in enumerate(lines):
        runs: list[tuple[int, str]] = []
        for cluster in _clusters(content):
            selected: int | None = None
            for index, font in enumerate(fonts):
                infos, _ = _shape(font, cluster)
                if all(info.codepoint != 0 for info in infos):
                    selected = index
                    break
            if selected is None:
                raise ValueError(f"Font candidates lack glyphs needed for {cluster!r}.")
            if runs and runs[-1][0] == selected:
                runs[-1] = (selected, runs[-1][1] + cluster)
            else:
                runs.append((selected, cluster))
        shaped = [(index, *_shape(fonts[index], run)) for index, run in runs]
        width = sum(
            sum(p.x_advance for p in positions) * scales[index] for index, _, positions in shaped
        )
        widths.append(width)
        x = -width / 2 if align == "center" else -width if align == "right" else 0
        y = -row * size * PT_TO_MM * line_spacing
        for index, infos, positions in shaped:
            used.add(index)
            scale = scales[index]
            file, collection, _, _ = files[index]
            for info, position in zip(infos, positions, strict=True):
                outline = glyph_path(file, collection, info.codepoint)
                placement = Transform.translate(
                    x + position.x_offset * scale, y + position.y_offset * scale
                ) @ Transform.scale(scale)
                path.extend(transform_path(outline, placement))
                x += position.x_advance * scale
                y += position.y_advance * scale
    selected_fonts = used or {0}
    ascender = max(fonts[i].get_font_extents("ltr").ascender * scales[i] for i in selected_fonts)
    descender = min(fonts[i].get_font_extents("ltr").descender * scales[i] for i in selected_fonts)
    width = max(widths, default=0)
    left = -width / 2 if align == "center" else -width if align == "right" else 0
    box = Bounds(
        left, descender - (len(lines) - 1) * size * PT_TO_MM * line_spacing, left + width, ascender
    )
    return TextLayout(
        box, geometry_bounds(path), tuple(widths), tuple(files[i][0] for i in sorted(used)), path
    )


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
    font: Font | FontStack | None = None
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
        selected = (
            self.font.fonts
            if isinstance(self.font, FontStack)
            else (self.font,)
            if isinstance(self.font, Font)
            else _font_context.get()
        )
        if not selected:
            raise ValueError("Specify Text.font or Canvas fonts before measuring text.")
        files: list[FontKey] = []
        for font in selected:
            file = FilePath(font.file).resolve()
            stat = file.stat()
            files.append((str(file), font.index, stat.st_mtime_ns, stat.st_size))
        return _layout(tuple(files), self.text, self.size, self.align, self.line_spacing)

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
