"""Complete basic paint values without Entity inheritance or default resolution."""

from dataclasses import dataclass
from math import isfinite
from typing import Literal

from pdl.author.style.color import BLACK, Color

type LineCap = Literal["butt", "round", "square"]
type LineJoin = Literal["miter", "round", "bevel"]
type FillRule = Literal["nonzero", "evenodd"]


@dataclass(frozen=True)
class Style:
    """Immutable solid fill, stroke, and opacity settings.

    Style is a value description, not an object relationship or rendering
    operation. Fields describe a complete style; they do not request field-wise
    inheritance. ``stroke=None`` and ``fill=None`` explicitly disable those
    paints. This is distinct from an Entity storing ``style=None``, which will
    request its Group or type default once Entities are implemented.

    The constructor defaults to a black 1 mm outline and no fill. These are
    Style-constructor defaults, not prescribed defaults for every Entity type.
    Construct a new value or use ``dataclasses.replace`` to change fields.
    Gradient paint, typography, object-level defaults, and group compositing
    are outside this checkpoint. Style does not resolve geometry or transform
    any of its values automatically.

    Args:
        stroke: Opaque outline color, or None to omit the outline.
        fill: Opaque interior color, or None to omit filling.
        line_width: Nonnegative stroke width in millimeters; zero omits stroke.
        line_cap: Shape of open line ends: butt, round, or square.
        line_join: Shape of line joins: miter, round, or bevel.
        fill_rule: Nonzero winding or even-odd interpretation of closed regions.
        opacity: Finite opacity in [0, 1], from transparent to opaque. Its
            application to a drawing or group belongs to the consuming object.

    Raises:
        ValueError: Width or opacity is invalid, or a named option is unsupported.
    """

    stroke: Color | None = BLACK
    fill: Color | None = None
    line_width: float = 1
    line_cap: LineCap = "butt"
    line_join: LineJoin = "miter"
    fill_rule: FillRule = "nonzero"
    opacity: float = 1

    def __post_init__(self) -> None:
        if not isfinite(self.line_width) or self.line_width < 0:
            raise ValueError("Line width must be finite and nonnegative.")
        if not isfinite(self.opacity) or not 0 <= self.opacity <= 1:
            raise ValueError("Opacity must be finite and between zero and one.")
        if self.line_cap not in ("butt", "round", "square"):
            raise ValueError("Unknown line cap.")
        if self.line_join not in ("miter", "round", "bevel"):
            raise ValueError("Unknown line join.")
        if self.fill_rule not in ("nonzero", "evenodd"):
            raise ValueError("Unknown fill rule.")
