"""Content-sized nodes and explicit, non-routing connectors."""

from __future__ import annotations

from dataclasses import dataclass
from math import hypot, isfinite, sqrt
from typing import Literal

from pdl.geometry.bounds import Anchor, Bounds
from pdl.geometry.primitives import Circle, Point, Position, Rectangle, point
from pdl.geometry.transforms import Transform
from pdl.scene.composition import Drawing
from pdl.scene.paint import BLACK, Style
from pdl.typography.plain import Text
from pdl.typography.tex import TeX


@dataclass(frozen=True)
class Node:
    """A rectangle or circle sized around measured Text/TeX content.

    Anchors describe the shape boundary, without stroke expansion. Label
    positioning uses its layout box rather than its visible ink contours.
    """

    label: Text | TeX
    position: Position = (0, 0)
    shape: Literal["rectangle", "circle"] = "rectangle"
    padding: tuple[float, float] = (2, 1.5)
    min_width: float = 0
    min_height: float = 0
    style: Style = Style(line_width=0.4)
    text_style: Style = Style(stroke=None, fill=BLACK)

    def __post_init__(self) -> None:
        point(self.position)
        if self.shape not in ("rectangle", "circle"):
            raise ValueError("Node shape must be rectangle or circle.")
        if not all(
            isfinite(v) and v >= 0 for v in (*self.padding, self.min_width, self.min_height)
        ):
            raise ValueError("Node padding and minimum dimensions must be finite and nonnegative.")

    @property
    def bounds(self) -> Bounds:
        label = self.label.layout_bounds
        width = max(self.min_width, label.width + 2 * self.padding[0])
        height = max(self.min_height, label.height + 2 * self.padding[1])
        if self.shape == "circle":
            width = height = max(
                hypot(label.width + 2 * self.padding[0], label.height + 2 * self.padding[1]),
                self.min_width,
                self.min_height,
            )
        p = point(self.position)
        return Bounds(p.x - width / 2, p.y - height / 2, p.x + width / 2, p.y + height / 2)

    def anchor(self, name: Anchor = "center") -> Point:
        box = self.bounds
        target = box.anchor(name)
        if self.shape == "circle" and " " in name:
            center = box.anchor()
            return Point(
                center.x + (target.x - center.x) / sqrt(2),
                center.y + (target.y - center.y) / sqrt(2),
            )
        return target

    def decompose(self) -> tuple[Drawing, ...]:
        box = self.bounds
        center = box.anchor()
        shape = (
            Circle(center, box.width / 2)
            if self.shape == "circle"
            else Rectangle((box.left, box.bottom), box.width, box.height)
        )
        label_center = self.label.layout_bounds.anchor()
        placement = Transform.translate(center.x - label_center.x, center.y - label_center.y)
        return Drawing(shape, self.style), Drawing(self.label, self.text_style, placement)
