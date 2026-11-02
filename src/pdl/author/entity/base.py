"""Thin editable drawing instances around current geometry and optional paint."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import replace
from typing import TYPE_CHECKING, ClassVar, Protocol, Self, runtime_checkable
from warnings import warn

from pdl.author.geometry.base import Geometry
from pdl.author.geometry.bounds import Anchor, Bounds
from pdl.author.geometry.point import Point, Position, as_point
from pdl.author.geometry.queries import bounds_of, ink_bounds_of, reference_of
from pdl.author.geometry.tex import TeX as TeXGeometry
from pdl.author.geometry.text import Text as TextGeometry
from pdl.author.style.color import BLACK
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
    Geometry subclasses declare membership without requiring shared operations.
    All positions are world coordinates in millimeters. Style None remains None
    until an operation explicitly changes paint or submission captures it.
    """

    default_style: ClassVar[Style] = Style()
    geometry_defaults: ClassVar[dict[type[Geometry], Style]] = {
        TextGeometry: Style(stroke=None, fill=BLACK),
        TeXGeometry: Style(stroke=None, fill=BLACK),
    }

    def __init__(
        self,
        geometry: Geometry,
        *,
        style: Style | None = None,
        reference: Position | None = None,
        default_style: Style | None = None,
    ) -> None:
        # Enforce nominal membership for callers without static type checking.
        if not isinstance(geometry, Geometry):  # pyright: ignore[reportUnnecessaryIsInstance]
            raise TypeError("Entity requires a Geometry instance.")
        self._default_style = default_style
        self._style_kind = type(geometry)
        self._geometry = geometry
        self._style = style
        self._reference = as_point(reference) if reference is not None else None
        self._parent: Group | None = None
        self._layer: object | None = None
        self._automatic_layer = True

    @property
    def geometry(self) -> Geometry:
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
        return self.default_paint

    @property
    def default_paint(self) -> Style:
        """Return the current own default before considering ancestor paint."""
        if self._default_style is not None:
            return self._default_style
        if type(self) is Entity:
            return self.geometry_defaults.get(self._style_kind, self.default_style)
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
        return ink_bounds_of(self.geometry)

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
            style = transform_style(
                target.style, target.effective_style, transform, target.geometry
            )
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

    def copy(self, *, default_style: Style | None = None) -> Self:
        """Copy geometry/members and detach root ownership and layer identity.

        Args:
            default_style: Optional own-default override, used when capture fixes
                resource/default policy while preserving an unset explicit style.
        """
        memo: dict[int, object] = {}
        if self.parent is not None:
            memo[id(self.parent)] = None
        if isinstance(self._layer, LayerRegistration):
            memo[id(self._layer)] = None
        result = deepcopy(self, memo)
        result._layer = None
        result._automatic_layer = True
        if default_style is not None:
            result._default_style = default_style
        return result

    def set_opacity(self, opacity: float) -> Self:
        return self.set_style(replace(self.effective_style, opacity=opacity))

    @property
    def root(self) -> Entity:
        result: Entity = self
        while result.parent is not None:
            result = result.parent
        return result

    @property
    def layer(self) -> object:
        value = self.root._layer
        return 0 if value is None else value

    @property
    def automatic_layer(self) -> bool:
        return self.root._automatic_layer

    def bind_layer(self, layer: object, *, automatic: bool) -> None:
        """Bind a Canvas identity while retaining integer-assignment semantics."""
        root = self.root
        root._layer = layer
        root._automatic_layer = automatic
        if isinstance(layer, LayerRegistration):
            layer.register(root)

    def set_layer(self, layer: object) -> Self:
        """Assign a paint layer to the outermost ownership unit."""
        integer = isinstance(layer, int) and not isinstance(layer, bool)
        if not integer and not isinstance(layer, LayerRegistration):
            raise TypeError("Expected an integer layer or Layer identity.")
        if self.root is not self:
            warn("Layer target promoted to its outermost Group.", UserWarning, stacklevel=2)
        self.bind_layer(layer, automatic=integer)
        return self


type TransformEdit = tuple[Entity, Geometry, Point, Style | None]


@runtime_checkable
class LayerRegistration(Protocol):
    @property
    def position(self) -> int: ...
    @property
    def stack(self) -> object | None: ...
    def register(self, member: Entity) -> None: ...
    def unregister(self, member: Entity) -> None: ...
