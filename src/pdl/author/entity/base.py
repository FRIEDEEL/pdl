"""Thin editable drawing instances around current geometry and optional paint."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import replace
from typing import TYPE_CHECKING, ClassVar, Self

from pdl.author.geometry.bounds import Anchor, Bounds
from pdl.author.geometry.point import Point, Position, as_point
from pdl.author.geometry.queries import bounds_of, reference_of
from pdl.author.style.style import Style
from pdl.author.transform.affine import (
    Reflection,
    Rescale,
    Rotation,
    Scaling,
    Translation,
)
from pdl.author.transform.base import Transform
from pdl.author.transform.operations import transform_geometry, transform_style

if TYPE_CHECKING:
    from pdl.author.entity.group import Group


class Entity:
    """A drawing object; geometry may change representation after transformation.

    Construction keeps the supplied geometry by reference. Transforms replace
    this instance's geometry, so other instances sharing the original are not
    changed. Explicit edits to a shared mutable Path still affect all holders.
    All positions are world coordinates in millimeters. Style None remains None
    until an operation explicitly changes paint or submission captures it.
    """

    default_style: ClassVar[Style] = Style()

    def __init__(
        self, geometry: object, *, style: Style | None = None, reference: Position | None = None
    ) -> None:
        self._geometry = geometry
        self._style = style
        self._reference = as_point(reference) if reference is not None else None
        self._parent: Group | None = None
        self._layer: object | None = None

    @property
    def geometry(self) -> object:
        return self._geometry

    @property
    def style(self) -> Style | None:
        return self._style

    @property
    def parent(self) -> Group | None:
        return self._parent

    @property
    def effective_style(self) -> Style:
        if self.style is not None:
            return self.style
        ancestor = self.parent
        while ancestor is not None:
            if ancestor.style is not None:
                return ancestor.style
            ancestor = ancestor.parent
        return type(self).default_style

    def set_style(self, style: Style | None) -> Self:
        """Set only this instance; None restores parent/type fallback."""
        self._style = style
        return self

    @property
    def reference(self) -> Point:
        return self._reference if self._reference is not None else reference_of(self.geometry)

    def set_reference(self, position: Position) -> Self:
        """Change the pivot for subsequent operations without moving geometry."""
        self._reference = as_point(position)
        return self

    @property
    def bounds(self) -> Bounds:
        return bounds_of(self.geometry)

    @property
    def ink_bounds(self) -> Bounds:
        return self.bounds

    def anchor(self, name: Anchor = "center") -> Point:
        return self.bounds.anchor(name)

    @property
    def center(self) -> Point:
        return self.anchor()

    @property
    def top(self) -> Point:
        return self.anchor("north")

    @property
    def bottom(self) -> Point:
        return self.anchor("south")

    @property
    def left(self) -> Point:
        return self.anchor("west")

    @property
    def right(self) -> Point:
        return self.anchor("east")

    def _transform_entities(self) -> tuple[Entity, ...]:
        return (self,)

    def prepare_transform(self, transform: Transform) -> list[TransformEdit]:
        """Prepare a transaction without mutating any target."""
        plans: list[TransformEdit] = []
        for target in self._transform_entities():
            reference = target.reference
            geometry = transform_geometry(target.geometry, transform)
            new_reference = Point(*transform.apply((reference.x, reference.y)))
            style = transform_style(target.style, target.effective_style, transform)
            plans.append((target, geometry, new_reference, style))
        return plans

    @staticmethod
    def commit_transform(plans: list[TransformEdit]) -> None:
        """Apply a validated transaction; used by explicit Gather selections."""
        for target, geometry, reference, style in plans:
            target._geometry, target._reference, target._style = geometry, reference, style

    def apply_transform(self, transform: Transform) -> Self:
        """Plan geometry conversions first, then apply the complete edit."""
        self.commit_transform(self.prepare_transform(transform))
        return self

    def translate(self, x: float, y: float) -> Self:
        return self.apply_transform(Translation(x, y))

    def move_to(self, position: Position, *, anchor: Anchor | None = None) -> Self:
        """Move the reference (or named bounds anchor) to a fixed position."""
        target = as_point(position)
        source = self.reference if anchor is None else self.anchor(anchor)
        return self.translate(target.x - source.x, target.y - source.y)

    def place(self, position: Position, *, anchor: Anchor | None = None) -> Self:
        return self.move_to(position, anchor=anchor)

    def rotate(self, angle: float, *, origin: Position | None = None) -> Self:
        return self.apply_transform(
            Rotation(angle).around(self.reference if origin is None else origin)
        )

    def scale(self, x: float, y: float | None = None, *, origin: Position | None = None) -> Self:
        return self.apply_transform(
            Scaling(x, y).around(self.reference if origin is None else origin)
        )

    def rescale(
        self, factor: float, *, include_linewidth: bool = False, origin: Position | None = None
    ) -> Self:
        pivot = self.reference if origin is None else as_point(origin)
        return self.apply_transform(
            Rescale(factor, include_linewidth=include_linewidth).around(pivot)
        )

    def reflect(self, angle: float = 0, *, origin: Position | None = None) -> Self:
        return self.apply_transform(
            Reflection(angle).around(self.reference if origin is None else origin)
        )

    def copy(self) -> Self:
        """Deep-copy geometry and children, excluding ownership and layer identity."""
        memo: dict[int, object] = {}
        if self.parent is not None:
            memo[id(self.parent)] = None
        if self._layer is not None:
            memo[id(self._layer)] = None
        return deepcopy(self, memo)

    def set_opacity(self, opacity: float) -> Self:
        return self.set_style(replace(self.effective_style, opacity=opacity))

    def set_layer(self, layer: object) -> Self:
        self._layer = layer
        return self


type TransformEdit = tuple[Entity, object, Point, Style | None]
