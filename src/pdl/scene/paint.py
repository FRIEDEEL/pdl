"""Backend-independent solid paint properties."""

from dataclasses import dataclass
from math import isfinite
from typing import Literal


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
