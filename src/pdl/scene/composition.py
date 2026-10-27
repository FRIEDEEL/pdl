"""Reusable composites, explicit placement and ordered scene traversal."""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from typing import TYPE_CHECKING, Protocol, Self, runtime_checkable

if TYPE_CHECKING:
    from pdl.scene.authoring import Entity
    from pdl.scene.layers import Layer

from pdl.geometry.bounds import Anchor, Bounds
from pdl.geometry.primitives import Geometry
from pdl.geometry.transforms import Transform
from pdl.scene.evaluation import layout_session
from pdl.scene.paint import Style
from pdl.scene.references import AnchorRef


@runtime_checkable
class Composite(Protocol):
    """An authoring object that decomposes to styled child drawings."""

    def decompose(self) -> tuple[Drawing, ...]: ...


type Graphic = Geometry | Composite


@dataclass(frozen=True)
class Drawing:
    """An object with optional instance paint and local affine placement.

    Args:
        geometry: Shape, text, or composite definition to place.
        style: Whole-style override; ``None`` allows inherited or object defaults.
        transform: Local-to-parent matrix, identity by default.

    This frozen record does not freeze arbitrary user-owned mutable objects.
    Canvas.draw captures built-in mutable descriptions when recording it.
    """

    geometry: Graphic
    style: Style | None = None
    transform: Transform = Transform()

    def anchor(self, name: Anchor = "center") -> AnchorRef:
        """Reference this instance, including its explicit placement."""
        return AnchorRef(self, name)

    def transformed(self, transform: Transform) -> Drawing:
        """Return a new Drawing with the matrix applied outside its current placement."""
        return Drawing(self.geometry, self.style, transform @ self.transform)

    def child(self, index: int) -> Drawing:
        """Address a Group child with this instance's accumulated placement."""
        from pdl.scene.authoring import Placement

        if isinstance(self.geometry, Placement):
            placed = self.geometry.placed()
            return Drawing(
                placed.geometry,
                self.style if self.style is not None else placed.style,
                self.transform @ placed.transform,
            ).child(index)
        if not isinstance(self.geometry, (Group, GroupDescription)):
            raise TypeError("Only an explicitly defined Group has addressable children.")
        child = self.geometry.child(index).transformed(self.transform)
        while isinstance(child.geometry, Placement):
            placed = child.geometry.placed()
            child = Drawing(
                placed.geometry,
                child.style if child.style is not None else placed.style,
                child.transform @ placed.transform,
            )
        return Drawing(
            child.geometry,
            child.style if child.style is not None else self.style,
            child.transform,
        )


@dataclass(frozen=True)
class GroupDescription:
    """An ordered reusable assembly of Drawing records.

    Args:
        children: Drawings in paint order, expressed in group-local coordinates.
        transform: Group-local to parent matrix, identity by default.

    The Group record is immutable, but child paths can remain mutable until
    captured by Canvas.draw. Explicit child styles override inherited styles
    as a whole. Group transforms move members together without recomputing spacing.
    Its anchor refers to axis-aligned group bounds; use child anchors for ports.
    """

    children: tuple[Drawing, ...]
    transform: Transform = Transform()
    style: Style | None = None

    def decompose(self) -> tuple[Drawing, ...]:
        return tuple(
            Drawing(
                child.geometry,
                child.style if child.style is not None else self.style,
                self.transform @ child.transform,
            )
            for child in self.children
        )

    def transformed(self, transform: Transform) -> GroupDescription:
        """Return a new Group with an outer matrix, leaving this definition unchanged."""
        return GroupDescription(self.children, transform @ self.transform, self.style)

    def child(self, index: int) -> Drawing:
        """Address a child in this group's parent coordinate space."""
        return self.children[index].transformed(self.transform)

    @property
    def bounds(self) -> Bounds:
        """Measure authoring layout bounds under the current typography context.

        For canvas-configured measurements, prefer ``canvas.query().bounds(...)``.
        """
        return bounds(self)

    def anchor(self, name: Anchor = "center") -> AnchorRef:
        """Reference the axis-aligned bounds of this placed group."""
        return AnchorRef(self, name)


class Group:
    """An editable, single-parent assembly with local coordinates.

    Args:
        children: Existing Entity/Group instances, or independent Drawing definitions.
            Existing instances retain their world placement. Drawing definitions use
            this group's local coordinates and create independent Entity instances.
        transform: Initial local-to-parent matrix.
        style: Inherited whole-style default; explicit member styles take precedence.
        layer: Target Layer or integer position. Omission chooses the highest member
            layer. The outermost group is always the layer and Gather operation unit.

    Adding, removing, and dismissing preserve placement and effective style.
    Mutations affect future captures only. ``transformed`` creates an independent
    reusable description; ``translate``, ``rotate``, and ``scale`` mutate this group.
    """

    def __init__(
        self,
        children: tuple[Drawing | Entity | Group, ...] = (),
        transform: Transform = Transform(),
        *,
        style: Style | None = None,
        layer: int | Layer | None = None,
    ) -> None:
        from pdl.scene.authoring import Entity
        from pdl.scene.layers import highest_layer

        self.parent: Group | None = None
        self.transform = transform
        self.style = style
        self._members: list[Entity | Group] = []
        from pdl.scene.layers import layer_position

        candidates = [c for c in children if not isinstance(c, Drawing)]
        children = tuple(
            sorted(children, key=lambda c: 0 if isinstance(c, Drawing) else layer_position(c.layer))
        )
        self.assigned_layer: int | Layer = highest_layer(candidates) if layer is None else layer
        self._dismissed = False
        for child in children:
            if isinstance(child, Drawing):
                member = Entity(child.geometry, style=child.style)
                member.placement = member.placement.__class__(
                    Drawing(member.placement.drawing.geometry, child.style, child.transform)
                )
                member.parent = self
                self._members.append(member)
            else:
                self.add(child)
        self.set_layer(self.assigned_layer)

    @property
    def members(self) -> tuple[Entity | Group, ...]:
        """Return direct live members in internal paint order."""
        return tuple(self._members)

    @property
    def children(self) -> tuple[Drawing, ...]:
        """Return captured direct members in group-local coordinates."""
        return tuple(
            Drawing(member.local_snapshot(), member.placement.paint)
            if not isinstance(member, Group)
            else Drawing(member._description())
            for member in self._members
        )

    @property
    def root(self) -> Group:
        """Return the outermost containing group."""
        return self if self.parent is None else self.parent.root

    @property
    def layer(self) -> int | Layer:
        """Return the effective layer of the outermost group."""
        return self.root.assigned_layer

    @property
    def world_transform(self) -> Transform:
        """Return the accumulated local-to-world matrix."""
        return (
            self.transform if self.parent is None else self.parent.world_transform @ self.transform
        )

    @property
    def effective_style(self) -> Style | None:
        return (
            self.style
            if self.style is not None or self.parent is None
            else self.parent.effective_style
        )

    def _description(self) -> GroupDescription:
        return GroupDescription(self.children, self.transform, self.style)

    def snapshot(self) -> GroupDescription:
        """Capture world placement and inherited paint without measuring text."""
        return GroupDescription(self.children, self.world_transform, self.effective_style)

    def decompose(self) -> tuple[Drawing, ...]:
        return self.snapshot().decompose()

    def child(self, index: int) -> Drawing:
        """Capture a child with accumulated world placement and inherited style."""
        from pdl.scene.authoring import Placement

        child = self.children[index].transformed(self.world_transform)
        while isinstance(child.geometry, Placement):
            placed = child.geometry.placed()
            child = Drawing(
                placed.geometry,
                child.style if child.style is not None else placed.style,
                child.transform @ placed.transform,
            )
        return Drawing(
            child.geometry,
            child.style if child.style is not None else self.effective_style,
            child.transform,
        )

    @property
    def bounds(self) -> Bounds:
        return bounds(self.snapshot())

    def anchor(self, name: Anchor = "center") -> AnchorRef:
        """Capture an axis-aligned group bounds anchor; later edits do not follow."""
        return AnchorRef(self.snapshot(), name)

    def set_layer(self, layer: int | Layer) -> Self:
        """Assign the whole outermost group to a layer; promote nested targets."""
        from pdl.scene.layers import assign_layer

        assign_layer(self, layer)
        return self

    def add(self, member: Entity | Group) -> Self:
        """Reparent an instance, preserving world placement and effective paint.

        Cycles are rejected. Existing direct members are left in place.
        """
        from pdl.scene.authoring import Placement

        if self._dismissed:
            raise ValueError("Cannot add members to a dismissed Group.")
        ancestor: Group | None = self
        while ancestor is not None:
            if ancestor is member:
                raise ValueError("Cyclic Group membership.")
            ancestor = ancestor.parent
        if member.parent is self:
            return self
        inverse = self.world_transform.inverse()
        world = member.world_transform if isinstance(member, Group) else Transform()
        paint = member.effective_style if isinstance(member, Group) else None
        state = member.snapshot()
        if member.parent is not None:
            member.parent.remove(member)
        if isinstance(member, Group):
            member.transform = inverse @ world
            member.style = paint
        else:
            member.placement = Placement(Drawing(state, transform=inverse))
        member.parent = self
        self._members.append(member)
        return self

    def remove(self, member: Entity | Group) -> Self:
        """Detach one direct member into world space, retaining this group's layer."""
        from pdl.scene.authoring import Placement

        if member not in self._members:
            raise ValueError("Instance is not a direct Group member.")
        layer = self.layer
        if isinstance(member, Group):
            world, paint = member.world_transform, member.effective_style
            member.parent = None
            member.transform, member.style = world, paint
        else:
            state = member.snapshot()
            member.parent = None
            member.placement = Placement(Drawing(state))
        self._members.remove(member)
        member.set_layer(layer)
        return self

    def dismiss(self) -> tuple[Entity | Group, ...]:
        """Dissolve this level, promoting members while preserving placement/paint.

        The emptied group is retired and rejects further additions. Nested groups
        remain intact. Existing Canvas captures are unaffected.
        """
        parent = self.parent
        members = self.members
        index = parent._members.index(self) if parent is not None else 0
        for member in members:
            self.remove(member)
        if parent is not None:
            parent.remove(self)
            for member in members:
                parent.add(member)
                parent._members.remove(member)
            parent._members[index:index] = members
        from pdl.scene.layers import Layer

        if isinstance(self.assigned_layer, Layer):
            self.assigned_layer.registrations.pop(id(self), None)
        self._dismissed = True
        return members

    def apply_transform(self, transform: Transform) -> Self:
        """Apply an affine matrix in authoring world space."""
        parent = Transform() if self.parent is None else self.parent.world_transform
        self.transform = parent.inverse() @ transform @ parent @ self.transform
        return self

    def translate(self, x: float, y: float) -> Self:
        """Translate by world millimeters."""
        return self.apply_transform(Transform.translate(x, y))

    def rotate(self, angle: float, *, center: tuple[float, float] = (0, 0)) -> Self:
        """Rotate in degrees about a world point, defaulting to the origin."""
        return self.apply_transform(Transform.rotate(angle).around(center))

    def scale(
        self, x: float, y: float | None = None, *, center: tuple[float, float] = (0, 0)
    ) -> Self:
        """Scale about a world point; stroke widths remain Canvas millimeters."""
        return self.apply_transform(Transform.scale(x, y).around(center))

    def reflect(self, angle: float = 0, *, origin: tuple[float, float] = (0, 0)) -> Self:
        """Reflect about a world line."""
        return self.apply_transform(Transform.reflect(angle, origin))

    def transformed(self, transform: Transform) -> GroupDescription:
        """Return an independent captured description with an outer transform."""
        return self.snapshot().transformed(transform)


def walk(
    drawings: tuple[Drawing, ...],
    transform: Transform = Transform(),
    style: Style | None = None,
    ancestors: frozenset[int] = frozenset(),
) -> Iterator[Drawing]:
    """Traverse composites without discarding leaf object identity."""
    with layout_session() as context:
        for drawing in drawings:
            placement = transform @ drawing.transform
            paint = drawing.style if drawing.style is not None else style
            geometry = drawing.geometry
            if isinstance(geometry, Composite):
                if id(geometry) in ancestors:
                    raise ValueError("Cyclic composite graph.")
                yield from walk(
                    context.decompose(geometry), placement, paint, ancestors | {id(geometry)}
                )
            else:
                yield Drawing(geometry, paint, placement)


def bounds(graphic: Graphic | Drawing) -> Bounds:
    """Measure authoring axis-aligned geometry/layout bounds without stroke.

    Args:
        graphic: Shape, text, composite, or placed Drawing.

    Returns:
        Bounds before Canvas viewport adaptation. Typography uses the current
        context; prefer ``canvas.query().bounds`` when canvas fonts/mappings matter.
    """
    with layout_session() as context:
        return context.bounds(graphic)
