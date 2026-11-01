"""Explicit-font text shaping, measurement and vector outline fallback."""

from __future__ import annotations

import unicodedata
from collections.abc import Callable, Generator
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path as FilePath

import uharfbuzz as hb

from pdl.foundation.geometry.bounds import Bounds, geometry_bounds
from pdl.foundation.geometry.primitives import Path
from pdl.foundation.geometry.transforms import Transform, transform_path
from pdl.foundation.typography.fonts import glyph_path

# Use TeX points consistently for both ordinary text and TeX fragments.
PT_TO_MM = 25.4 / 72.27


@dataclass(frozen=True)
class Font:
    """An explicit static font file, optionally indexed within a collection.

    Args:
        file: Existing TTF, OTF, or TTC file path.
        index: Nonnegative face index for a font collection, default zero.

    Raises:
        FileNotFoundError: The file does not exist.
        ValueError: The collection index is negative.

    This constructor does not resolve family names. Use RendererConfig font
    candidates for discovery by installed family name.
    """

    file: str | FilePath
    index: int = 0

    def __post_init__(self) -> None:
        if self.index < 0:
            raise ValueError("Font index must be nonnegative.")
        if not FilePath(self.file).is_file():
            raise FileNotFoundError(self.file)


@dataclass(frozen=True)
class FontStack:
    """An ordered fallback list searched per combining sequence.

    Args:
        fonts: Nonempty tuple of explicit Font objects, in preference order.

    Raises:
        ValueError: The font list is empty.

    Every requested combining sequence must be supported by a candidate font;
    missing coverage is reported rather than silently dropping characters.
    """

    fonts: tuple[Font, ...]

    def __post_init__(self) -> None:
        if not self.fonts:
            raise ValueError("A FontStack needs at least one font.")


type FontPolicy = tuple[Font, ...] | Callable[[], tuple[Font, ...]]

font_policy: ContextVar[FontPolicy] = ContextVar("pdl_fonts", default=())


@contextmanager
def font_context(fonts: FontPolicy) -> Generator[None, None, None]:
    """Use task-local defaults for measurement and rendering together."""
    token = font_policy.set(fonts)
    try:
        yield
    finally:
        font_policy.reset(token)


@dataclass(frozen=True)
class TextRun:
    """A native text span with a resolved font and baseline position."""

    text: str
    font: Font
    x: float
    y: float


@dataclass(frozen=True)
class _GlyphPlacement:
    file: str
    index: int
    gid: int
    transform: Transform


@dataclass(frozen=True)
class TextLayout:
    """Backend-independent measurements; outlines are generated only on request."""

    box: Bounds
    advances: tuple[float, ...]
    fonts_used: tuple[str, ...]
    runs: tuple[TextRun, ...]
    _glyphs: tuple[_GlyphPlacement, ...]

    @property
    def ink(self) -> Bounds:
        return geometry_bounds(self.to_path())

    def to_path(self) -> Path:
        """Explicitly opt into outline conversion rather than native text."""
        path = Path()
        for glyph in self._glyphs:
            path.extend(
                transform_path(glyph_path(glyph.file, glyph.index, glyph.gid), glyph.transform)
            )
        return path


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
def measure_text(
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
    glyphs: list[_GlyphPlacement] = []
    native_runs: list[TextRun] = []
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
        shaped = [(index, run, *_shape(fonts[index], run)) for index, run in runs]
        width = sum(
            sum(p.x_advance for p in positions) * scales[index] for index, _, _, positions in shaped
        )
        widths.append(width)
        x = -width / 2 if align == "center" else -width if align == "right" else 0
        y = -row * size * PT_TO_MM * line_spacing
        for index, content, infos, positions in shaped:
            used.add(index)
            scale = scales[index]
            file, collection, _, _ = files[index]
            native_runs.append(TextRun(content, Font(file, collection), x, y))
            for info, position in zip(infos, positions, strict=True):
                placement = Transform.translate(
                    x + position.x_offset * scale, y + position.y_offset * scale
                ) @ Transform.scale(scale)
                glyphs.append(_GlyphPlacement(file, collection, info.codepoint, placement))
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
        box,
        tuple(widths),
        tuple(files[i][0] for i in sorted(used)),
        tuple(native_runs),
        tuple(glyphs),
    )
