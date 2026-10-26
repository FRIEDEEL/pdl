"""Narrow adapter around fontTools' untyped font/pen interfaces.

Only the dynamic third-party boundary uses scoped type-checking suppressions;
public authoring and layout APIs remain strictly typed.
"""

from functools import lru_cache
from pathlib import Path as FilePath
from typing import Protocol, cast

from fontTools.pens.basePen import BasePen  # pyright: ignore[reportMissingTypeStubs]
from fontTools.ttLib import TTFont  # pyright: ignore[reportMissingTypeStubs]

from pdl.geometry import Path

type Pair = tuple[float, float]


class _Glyph(Protocol):
    def draw(self, pen: object) -> None: ...


class _GlyphSet(Protocol):
    def __getitem__(self, key: str) -> _Glyph: ...


class _Font(Protocol):
    def getGlyphSet(self) -> _GlyphSet: ...
    def getGlyphName(self, glyphID: int) -> str: ...
    def close(self) -> None: ...


class _FontFactory(Protocol):
    def __call__(self, file: str, *, fontNumber: int) -> _Font: ...


class OutlinePen(BasePen):  # pyright: ignore[reportUntypedBaseClass]
    """Translate decomposed font contours to pdl path commands."""

    def __init__(self, glyphs: _GlyphSet | None = None) -> None:
        super().__init__(glyphs)  # pyright: ignore[reportUnknownMemberType]
        self.path = Path()

    def _moveTo(self, pt: Pair) -> None:
        self.path.move_to(pt)

    def _lineTo(self, pt: Pair) -> None:
        self.path.line_to(pt)

    def _curveToOne(self, pt1: Pair, pt2: Pair, pt3: Pair) -> None:
        self.path.cubic_to(pt1, pt2, pt3)

    def _qCurveToOne(self, pt1: Pair, pt2: Pair) -> None:
        self.path.quadratic_to(pt1, pt2)

    def _closePath(self) -> None:
        self.path.close()

    def _endPath(self) -> None:
        pass


@lru_cache(maxsize=512)
def _glyph(file: str, index: int, stamp: tuple[int, int], gid: int) -> Path:
    del stamp
    factory = cast(_FontFactory, TTFont)
    font = factory(file, fontNumber=index)
    try:
        glyphs = font.getGlyphSet()
        pen = OutlinePen(glyphs)
        glyphs[font.getGlyphName(gid)].draw(pen)
        return pen.path
    finally:
        font.close()


def glyph_path(file: str, index: int, gid: int) -> Path:
    """Return an independent outline snapshot for a shaped glyph ID."""
    stat = FilePath(file).stat()
    return _glyph(file, index, (stat.st_mtime_ns, stat.st_size), gid).to_path()
