"""Backend-independent normalized gradient descriptions."""

from dataclasses import dataclass
from math import isfinite

from pdl.author.style.color import Color


def validate_pair(pair: tuple[float, float]) -> None:
    if not all(isfinite(v) for v in pair):
        raise ValueError("Gradient coordinates must be finite.")


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
    start: tuple[float, float] = (0, 0)
    end: tuple[float, float] = (1, 0)
    frame: tuple[tuple[float, float], tuple[float, float], tuple[float, float]] | None = None

    def __post_init__(self) -> None:
        validate_stops(self.stops)
        if self.frame is not None:
            for point in self.frame:
                validate_pair(point)
        validate_pair(self.start)
        validate_pair(self.end)
        if self.start == self.end:
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
    center: tuple[float, float] = (0.5, 0.5)
    radius: float = 0.5
    frame: tuple[tuple[float, float], tuple[float, float], tuple[float, float]] | None = None

    def __post_init__(self) -> None:
        validate_stops(self.stops)
        if self.frame is not None:
            for point in self.frame:
                validate_pair(point)
        validate_pair(self.center)
        if not isfinite(self.radius) or self.radius <= 0:
            raise ValueError("Radial gradient radius must be positive and finite.")


type Fill = Color | LinearGradient | RadialGradient
