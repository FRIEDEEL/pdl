"""Backend-independent solid paint properties."""

from dataclasses import dataclass
from math import isfinite
from typing import Literal


@dataclass(frozen=True)
class Color:
    """An RGB color with channels between zero and one, inclusive.

    Args:
        red: Red channel; 0 means absent, 1 means full intensity.
        green: Green channel.
        blue: Blue channel.

    Raises:
        ValueError: A channel is nonfinite or outside the allowed range.
    """

    red: float
    green: float
    blue: float

    def __post_init__(self) -> None:
        if not all(isfinite(v) and 0 <= v <= 1 for v in (self.red, self.green, self.blue)):
            raise ValueError("Color channels must be between zero and one.")


BLACK = Color(0, 0, 0)


@dataclass(frozen=True)
class Style:
    """Solid fill and stroke settings shared by both output backends.

    Args:
        stroke: Outline color, or ``None`` to omit the outline. Defaults to black.
        fill: Interior color, or ``None`` to leave the interior unpainted.
        line_width: Nonnegative stroke width in Canvas millimeters; zero suppresses stroke.
        line_cap: Open line ends: ``butt``, ``round``, or ``square``.
        line_join: Corners: ``miter``, ``round``, or ``bevel``. Miter limit is 10.
        fill_rule: ``nonzero`` winding or ``evenodd`` crossing rule for interiors.

    Fill is painted before stroke. A style overrides inherited paint as a whole,
    not field by field. Native Text and TeX require fill-only paint: explicitly
    set ``stroke=None`` when supplying their style. Omitting their style uses
    black fill. TikZ aliases, opacity, and gradients are not implemented yet.

    Raises:
        ValueError: Width is negative/nonfinite or a named option is unsupported.
    """

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
