"""Content-sized nodes and explicit, non-routing connectors."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Literal

from pdl.geometry.bounds import Anchor, Bounds
from pdl.geometry.primitives import Circle, Rectangle, point
from pdl.geometry.transforms import Transform
from pdl.scene.composition import Drawing
from pdl.scene.evaluation import layout_session
from pdl.scene.paint import BLACK, Style
from pdl.scene.references import AnchorRef, PointSource
from pdl.typography.plain import Text
from pdl.typography.tex import TeX


@dataclass(frozen=True)
class Node:
    """A rectangle or circle sized around measured Text/TeX content.

    Anchors describe the shape boundary, without stroke expansion. Label
    positioning uses its layout box rather than its visible ink contours.
    """

    label: Text | TeX
    position: PointSource = (0, 0)
    shape: Literal["rectangle", "circle"] = "rectangle"
    padding: tuple[float, float] = (2, 1.5)
    min_width: float = 0
    min_height: float = 0
    style: Style = Style(line_width=0.4)
    text_style: Style = Style(stroke=None, fill=BLACK)

    def __post_init__(self) -> None:
        if not isinstance(self.position, AnchorRef):
            point(self.position)
        if self.shape not in ("rectangle", "circle"):
            raise ValueError("Node shape must be rectangle or circle.")
        if not all(
            isfinite(v) and v >= 0 for v in (*self.padding, self.min_width, self.min_height)
        ):
            raise ValueError("Node padding and minimum dimensions must be finite and nonnegative.")

    @property
    def bounds(self) -> Bounds:
        with layout_session() as context:
            return context.node_bounds(self)

    def anchor(self, name: Anchor = "center") -> AnchorRef:
        return AnchorRef(self, name)

    def decompose(self) -> tuple[Drawing, ...]:
        box = self.bounds
        center = box.anchor()
        shape = (
            Circle(center, box.width / 2)
            if self.shape == "circle"
            else Rectangle((box.left, box.bottom), box.width, box.height)
        )
        return Drawing(shape, self.style), self.label_drawing()

    def label_drawing(self) -> Drawing:
        """Place the label using the same layout as native and fallback output."""
        center = self.bounds.anchor()
        label_center = self.label.layout_bounds.anchor()
        placement = Transform.translate(center.x - label_center.x, center.y - label_center.y)
        return Drawing(self.label, self.text_style, placement)
