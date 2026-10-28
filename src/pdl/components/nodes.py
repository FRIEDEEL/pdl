"""Content-sized nodes and explicit, non-routing connectors."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Literal

from pdl.geometry.bounds import Anchor, Bounds
from pdl.geometry.primitives import Circle, Rectangle, point
from pdl.geometry.transforms import Transform
from pdl.scene.composition import Drawing
from pdl.scene.entity import Entity
from pdl.scene.evaluation import layout_session
from pdl.scene.paint import BLACK, Style
from pdl.scene.references import AnchorRef, PointSource
from pdl.scene.spaces import SpacePoint
from pdl.typography.plain import Text
from pdl.typography.tex import TeX


@dataclass(eq=False)
class Node(Entity):
    """A text label inside an automatically sized rectangle or circle.

    Args:
        label: Text or TeX content; measured when needed, not at construction.
        position: Shape center as coordinates or a deferred position reference.
        shape: ``rectangle`` or ``circle``.
        padding: Horizontal and vertical padding in millimeters, on each side.
        min_width: Nonnegative minimum width in millimeters.
        min_height: Nonnegative minimum height in millimeters.
        style: Shape paint, default black outline of width 0.4 mm.
        text_style: Fill-only label paint, default black.

    Anchors lie on the shape boundary before stroke expansion. Circle sizing
    contains the padded label box. Labels are centered using layout boxes,
    which can differ from visible glyph contours.
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
        if not isinstance(self.position, (AnchorRef, SpacePoint)):
            point(self.position)
        if self.shape not in ("rectangle", "circle"):
            raise ValueError("Node shape must be rectangle or circle.")
        if not all(
            isfinite(v) and v >= 0 for v in (*self.padding, self.min_width, self.min_height)
        ):
            raise ValueError("Node padding and minimum dimensions must be finite and nonnegative.")

    @property
    def bounds(self) -> Bounds:
        """Measure the node's authoring shape bounds using the current font context."""
        with layout_session() as context:
            return (
                context.node_bounds(self)
                if self.description_only
                else context.bounds(self.snapshot())
            )

    def anchor(self, name: Anchor = "center") -> AnchorRef:
        """Describe a center or compass point on the shape boundary, excluding stroke.

        The returned AnchorRef is measured with the eventual font configuration.
        """
        return AnchorRef(self, name) if self.description_only else super().anchor(name)

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
