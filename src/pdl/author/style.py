"""Backend-independent solid/gradient fills, strokes, and per-leaf opacity."""

from dataclasses import dataclass
from math import isfinite
from typing import Literal

from pdl.foundation.geometry.primitives import Position, point


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
class ColorStop:
    """An opaque RGB color at an offset between zero and one."""

    offset: float
    color: Color

    def __post_init__(self) -> None:
        if not isfinite(self.offset) or not 0 <= self.offset <= 1:
            raise ValueError("Gradient stop offset must be between zero and one.")


def validate_stops(stops: tuple[ColorStop, ...]) -> None:
    if len(stops) < 2 or stops[0].offset != 0 or stops[-1].offset != 1:
        raise ValueError("Gradients require at least two stops, starting at 0 and ending at 1.")
    if any(a.offset >= b.offset for a, b in zip(stops, stops[1:])):
        raise ValueError("Gradient stop offsets must be strictly increasing.")


@dataclass(frozen=True)
class LinearGradient:
    """RGB interpolation along a vector in normalized local geometry bounds.

    Args:
        stops: Strictly increasing color stops including offsets zero and one.
        start: Start point; (0, 0) is the local bounds' lower-left corner.
        end: End point; (1, 1) is the upper-right corner. Defaults left to right.

    Colors pad beyond the endpoints. The gradient follows object/group transforms.
    Only fill gradients are supported; stop opacity and alternate spread/color
    interpolation modes are not provided. Text/TeX require solid colors.
    """

    stops: tuple[ColorStop, ...]
    start: Position = (0, 0)
    end: Position = (1, 0)

    def __post_init__(self) -> None:
        validate_stops(self.stops)
        if point(self.start) == point(self.end):
            raise ValueError("Linear gradient endpoints must differ.")


@dataclass(frozen=True)
class RadialGradient:
    """Concentric RGB interpolation in normalized local geometry bounds.

    Args:
        stops: Strictly increasing stops including zero and one.
        center: Normalized center; defaults to the middle of the local bounds.
        radius: Positive normalized radius; default 0.5 reaches each side midpoint.

    Non-square bounds stretch the gradient into an ellipse. Colors pad beyond
    the radius. Focal offsets, stop opacity, and stroke gradients are unsupported.
    """

    stops: tuple[ColorStop, ...]
    center: Position = (0.5, 0.5)
    radius: float = 0.5

    def __post_init__(self) -> None:
        validate_stops(self.stops)
        point(self.center)
        if not isfinite(self.radius) or self.radius <= 0:
            raise ValueError("Radial gradient radius must be positive and finite.")


type Fill = Color | LinearGradient | RadialGradient


@dataclass(frozen=True)
class Style:
    """Fill and stroke settings shared by both output backends.

    Args:
        stroke: Outline color, or ``None`` to omit the outline. Defaults to black.
        fill: Interior Color, LinearGradient, RadialGradient, or ``None`` for no fill.
        line_width: Nonnegative stroke width in Canvas millimeters; zero suppresses stroke.
        line_cap: Open line ends: ``butt``, ``round``, or ``square``.
        line_join: Corners: ``miter``, ``round``, or ``bevel``. Miter limit is 10.
        fill_rule: ``nonzero`` winding or ``evenodd`` crossing rule for interiors.
        opacity: Per-leaf opacity between zero and one, default one. Overlapping
            members composite independently; this is not isolated group opacity.

    Fill is painted before stroke. A style overrides inherited paint as a whole,
    not field by field. Native Text and TeX require fill-only paint: explicitly
    set ``stroke=None`` when supplying their style. Omitting their style uses
    black fill. Gradient fills use normalized local geometry bounds; ordinary
    text and TeX accept solid fills only. TikZ aliases are not implemented.

    Raises:
        ValueError: Width is negative/nonfinite or a named option is unsupported.
    """

    stroke: Color | None = BLACK
    fill: Fill | None = None
    line_width: float = 1
    line_cap: Literal["butt", "round", "square"] = "butt"
    line_join: Literal["miter", "round", "bevel"] = "miter"
    fill_rule: Literal["nonzero", "evenodd"] = "nonzero"
    opacity: float = 1

    def __post_init__(self) -> None:
        if not isfinite(self.opacity) or not 0 <= self.opacity <= 1:
            raise ValueError("Opacity must be between zero and one.")
        if not isfinite(self.line_width) or self.line_width < 0:
            raise ValueError("Line width must be finite and nonnegative.")
        if self.line_cap not in ("butt", "round", "square"):
            raise ValueError("Unknown line cap.")
        if self.line_join not in ("miter", "round", "bevel"):
            raise ValueError("Unknown line join.")
        if self.fill_rule not in ("nonzero", "evenodd"):
            raise ValueError("Unknown fill rule.")
