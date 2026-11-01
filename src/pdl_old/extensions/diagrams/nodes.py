"""Content-sized nodes and explicit, non-routing connectors."""

from __future__ import annotations

from dataclasses import dataclass
from math import hypot, isfinite, sqrt
from typing import Literal

from pdl.author.composition import Drawing
from pdl.author.entity import Entity
from pdl.author.measurement import layout_session
from pdl.author.references import PointSource
from pdl.author.shapes import Circle, Rectangle
from pdl.author.spaces import SpacePoint
from pdl.author.style import BLACK, Style
from pdl.author.tex import TeX
from pdl.author.text import Text
from pdl.foundation.geometry.bounds import Anchor, Bounds
from pdl.foundation.geometry.primitives import Point, point
from pdl.foundation.geometry.transforms import Transform


@dataclass(eq=False)
class Node(Entity):
    """A text label inside an automatically sized rectangle or circle.

    Args:
        label: Text or TeX content; measured when needed, not at construction.
        position: Shape center as coordinates or an immediately evaluated frame point.
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
        if isinstance(self.position, SpacePoint):
            self.position = self.position.resolve()
        if not isinstance(self.position, SpacePoint):
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
            return self.layout_bounds if self.description_only else context.bounds(self.snapshot())

    @property
    def layout_bounds(self) -> Bounds:
        """Compute local shape bounds from the current measured label."""
        label = self.label.layout_bounds
        width = max(self.min_width, label.width + 2 * self.padding[0])
        height = max(self.min_height, label.height + 2 * self.padding[1])
        if self.shape == "circle":
            width = height = max(
                hypot(label.width + 2 * self.padding[0], label.height + 2 * self.padding[1]),
                self.min_width,
                self.min_height,
            )
        with layout_session() as context:
            p = context.point(self.position)
        return Bounds(p.x - width / 2, p.y - height / 2, p.x + width / 2, p.y + height / 2)

    def local_anchor(self, name: Anchor = "center") -> Point:
        """Measure the local shape boundary, including circular diagonals."""
        box = self.layout_bounds
        result = box.anchor(name)
        if self.shape == "circle" and " " in name:
            center = box.anchor()
            return Point(
                center.x + (result.x - center.x) / sqrt(2),
                center.y + (result.y - center.y) / sqrt(2),
            )
        return result

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
