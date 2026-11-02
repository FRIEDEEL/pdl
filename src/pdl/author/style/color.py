"""Opaque RGB color values, independent of geometry and output formats."""

from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True)
class Color:
    """An immutable RGB color with finite channels in the interval [0, 1].

    This value carries no opacity, geometry, or backend encoding. Opacity is a
    separate Style attribute. Color names, hex strings, gradients, and automatic
    conversion from other color models are not provided by this type.

    Args:
        red: Red channel, from zero to one inclusive.
        green: Green channel, from zero to one inclusive.
        blue: Blue channel, from zero to one inclusive.

    Raises:
        ValueError: Any channel is nonfinite or outside [0, 1].
    """

    red: float
    green: float
    blue: float

    def __post_init__(self) -> None:
        if not all(isfinite(value) and 0 <= value <= 1 for value in self.channels):
            raise ValueError("RGB channels must be finite and between zero and one.")

    @property
    def channels(self) -> tuple[float, float, float]:
        """Return the RGB channel values without converting to an output format."""
        return self.red, self.green, self.blue


BLACK = Color(0, 0, 0)
