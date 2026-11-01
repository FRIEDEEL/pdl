"""Narrow adapter around fontTools' untyped font/pen interfaces.

Only the dynamic third-party boundary uses scoped type-checking suppressions;
public authoring and layout APIs remain strictly typed.
"""

from functools import lru_cache
from pathlib import Path as FilePath
from typing import Protocol, cast

from fontTools.pens.basePen import BasePen  # pyright: ignore[reportMissingTypeStubs]
from fontTools.ttLib import TTFont  # pyright: ignore[reportMissingTypeStubs]

type Outline = tuple[tuple[str, tuple[tuple[float, float], ...]], ...]

type Pair = tuple[float, float]


class _Glyph(Protocol):
    def draw(self, pen: object) -> None: ...


class _GlyphSet(Protocol):
    def __getitem__(self, key: str) -> _Glyph: ...


class _NameTable(Protocol):
    def getBestFamilyName(self) -> str | None: ...


class _Font(Protocol):
    def __getitem__(self, key: str) -> _NameTable: ...
    def getGlyphSet(self) -> _GlyphSet: ...
    def getGlyphName(self, glyphID: int) -> str: ...
    def close(self) -> None: ...


class _FontFactory(Protocol):
    def __call__(self, file: str, *, fontNumber: int) -> _Font: ...


class OutlinePen(BasePen):  # pyright: ignore[reportUntypedBaseClass]
    """Translate decomposed font contours to pdl path commands."""

    def __init__(self, glyphs: _GlyphSet | None = None) -> None:
        super().__init__(glyphs)  # pyright: ignore[reportUnknownMemberType]
        self.commands: list[tuple[str, tuple[Pair, ...]]] = []

    def _moveTo(self, pt: Pair) -> None:
        self.commands.append(("M", (pt,)))

    def _lineTo(self, pt: Pair) -> None:
        self.commands.append(("L", (pt,)))

    def _curveToOne(self, pt1: Pair, pt2: Pair, pt3: Pair) -> None:
        self.commands.append(("C", (pt1, pt2, pt3)))

    def _qCurveToOne(self, pt1: Pair, pt2: Pair) -> None:
        self.commands.append(("Q", (pt1, pt2)))

    def _closePath(self) -> None:
        self.commands.append(("Z", ()))

    def _endPath(self) -> None:
        pass


@lru_cache(maxsize=512)
def _glyph(file: str, index: int, stamp: tuple[int, int], gid: int) -> Outline:
    del stamp
    factory = cast(_FontFactory, TTFont)
    font = factory(file, fontNumber=index)
    try:
        glyphs = font.getGlyphSet()
        pen = OutlinePen(glyphs)
        glyphs[font.getGlyphName(gid)].draw(pen)
        return tuple(pen.commands)
    finally:
        font.close()


def glyph_outline(file: str, index: int, gid: int) -> Outline:
    """Return an independent outline snapshot for a shaped glyph ID."""
    stat = FilePath(file).stat()
    return _glyph(file, index, (stat.st_mtime_ns, stat.st_size), gid)


@lru_cache(maxsize=64)
def _family(file: str, index: int, stamp: tuple[int, int]) -> str:
    del stamp
    factory = cast(_FontFactory, TTFont)
    font = factory(file, fontNumber=index)
    try:
        return font["name"].getBestFamilyName() or FilePath(file).stem
    finally:
        font.close()


def font_family(file: str, index: int = 0) -> str:
    """Read a native font-family name without generating glyph outlines."""
    stat = FilePath(file).stat()
    return _family(file, index, (stat.st_mtime_ns, stat.st_size))
