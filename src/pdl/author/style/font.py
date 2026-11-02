"""Explicit font resources, separate from loading and shaping."""

from dataclasses import dataclass
from pathlib import Path as FilePath


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
