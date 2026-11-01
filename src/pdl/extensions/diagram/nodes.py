"""Content-sized nodes expanded into ordinary owned Author entities."""

from __future__ import annotations

from math import hypot, isfinite, sqrt
from typing import Literal

from pdl.author.entity.base import Entity
from pdl.author.entity.factories import Circle, Rectangle, Text
from pdl.author.entity.group import Group
from pdl.author.geometry.bounds import Anchor, Bounds
from pdl.author.geometry.frame import SpacePoint
from pdl.author.geometry.point import Point, Position, as_point
from pdl.author.geometry.shapes import Circle as CircleGeometry
from pdl.author.style import BLACK, Style


class Node(Group):
    """A lazily sized node; first query, edit, or capture builds its actual members.

    The label is copied into the node. Before expansion, font/TeX measurement
    is deferred. Once expanded, the border and label are ordinary members and
    all transforms edit them immediately. Use rebuild after editing label content
    if the border should be sized again. Position is the node reference point.
    """

    def __init__(
        self,
        label: Entity | str,
        position: Position | SpacePoint = (0, 0),
        *,
        shape: Literal["rectangle", "circle"] = "rectangle",
        padding: tuple[float, float] = (2, 1.5),
        min_width: float = 0,
        min_height: float = 0,
        style: Style | None = Style(line_width=0.4),
        text_style: Style = Style(stroke=None, fill=BLACK),
    ) -> None:
        if shape not in ("rectangle", "circle"):
            raise ValueError("Node shape must be rectangle or circle.")
        if not all(isfinite(v) and v >= 0 for v in (*padding, min_width, min_height)):
            raise ValueError("Node dimensions and padding must be finite and nonnegative.")
        point = position.resolve() if isinstance(position, SpacePoint) else as_point(position)
        super().__init__(style=style, reference=point)
        self.label = Text(label) if isinstance(label, str) else label.copy()
        self.label.set_style(text_style)
        self.shape, self.padding = shape, padding
        self.min_width, self.min_height = min_width, min_height
        self._ready = False
        self._border: Entity | None = None

    @property
    def position(self) -> Point:
        return self.reference

    def _ensure_layout(self) -> None:
        if self._ready:
            return
        box = self.label.bounds
        width = max(self.min_width, box.width + 2 * self.padding[0])
        height = max(self.min_height, box.height + 2 * self.padding[1])
        center = self.reference
        if self.shape == "circle":
            diameter = max(
                hypot(box.width + 2 * self.padding[0], box.height + 2 * self.padding[1]),
                self.min_width,
                self.min_height,
            )
            self._border = Circle(center, diameter / 2)
        else:
            self._border = Rectangle((center.x - width / 2, center.y - height / 2), width, height)
        self.label.move_to(center, anchor="center")
        self.add(self._border, self.label)
        self._ready = True

    @property
    def members(self) -> tuple[Entity, ...]:
        self._ensure_layout()
        return super().members

    @property
    def bounds(self) -> Bounds:
        self._ensure_layout()
        assert self._border is not None
        return self._border.bounds

    @property
    def layout_bounds(self) -> Bounds:
        return self.bounds

    def anchor(self, name: Anchor = "center") -> Point:
        self._ensure_layout()
        assert self._border is not None
        geometry = self._border.geometry
        if isinstance(geometry, CircleGeometry) and " " in name:
            result = self.bounds.anchor(name)
            center = self.bounds.anchor()
            return Point(
                center.x + (result.x - center.x) / sqrt(2),
                center.y + (result.y - center.y) / sqrt(2),
            )
        return self.bounds.anchor(name)

    def local_anchor(self, name: Anchor = "center") -> Point:
        return self.anchor(name)

    def label_drawing(self) -> Entity:
        self._ensure_layout()
        return self.label.copy()

    def decompose(self) -> tuple[Entity, ...]:
        return tuple(member.copy() for member in self.members)

    def _transform_entities(self) -> tuple[Entity, ...]:
        self._ensure_layout()
        return super()._transform_entities()

    def rebuild(self) -> Node:
        """Rebuild an axis-aligned border around the label's current layout."""
        self._ensure_layout()
        for member in tuple(self._members):
            self.remove(member)
        self._ready = False
        self._ensure_layout()
        return self
