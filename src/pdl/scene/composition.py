"""Reusable composites, explicit placement and ordered scene traversal."""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from typing import TYPE_CHECKING, Protocol, Self, runtime_checkable

if TYPE_CHECKING:
    from pdl.scene.authoring import Placement
    from pdl.scene.layers import Layer
    from pdl.scene.references import PointSource
    from pdl.scene.spaces import CoordinateSystem

from pdl.geometry.bounds import Anchor, Bounds
from pdl.geometry.primitives import Geometry, Position
from pdl.geometry.transforms import Transform
from pdl.scene.entity import Entity
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
        child = self.children[index].transformed(self.transform)
        return Drawing(
            child.geometry, child.style if child.style is not None else self.style, child.transform
        )

    @property
    def bounds(self) -> Bounds:
        """Measure authoring layout bounds under the current typography context.

        For canvas-configured measurements, prefer ``canvas.query().bounds(...)``.
        """
        return bounds(self)

    def anchor(self, name: Anchor = "center") -> AnchorRef:
        """Reference the axis-aligned bounds of this placed group."""
        return AnchorRef(self, name)


class Group(Entity):
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
        from pdl.scene.authoring import Entity, Placement
        from pdl.scene.layers import highest_layer

        self.parent = None
        self.transform = transform
        self._operations: list[tuple[Transform, PointSource]] = []
        self.style = style
        self._members: list[Entity | Group] = []
        from pdl.scene.layers import layer_position

        candidates = [c for c in children if not isinstance(c, Drawing)]
        children = tuple(
            sorted(children, key=lambda c: 0 if isinstance(c, Drawing) else layer_position(c.layer))
        )
        self.assigned_layer = highest_layer(candidates) if layer is None else layer
        self._dismissed = False
        for child in children:
            if isinstance(child, Drawing):
                member = Entity(child.geometry, style=child.style)
                member.placement = Placement(
                    Drawing(member.placement.drawing.geometry, child.style, child.transform)
                )
                member.parent = self
                self._members.append(member)
            else:
                self.add(child)
        self.set_layer(self.assigned_layer)

    @property
    def parent(self) -> Group | None:
        return self._parent

    @parent.setter
    def parent(self, value: Group | None) -> None:
        self._parent = value

    @property
    def assigned_layer(self) -> int | Layer:
        return self._assigned_layer

    @assigned_layer.setter
    def assigned_layer(self, value: int | Layer) -> None:
        self._assigned_layer = value

    def copy(self) -> Self:
        """Copy the assembly and members independently, retaining world placement."""
        from copy import deepcopy

        result = deepcopy(self)
        result.parent = None
        if self.parent is not None:
            result.transform = self.world_transform
            result._operations = []
        result.style = self.effective_style
        return result

    @property
    def dismissed(self) -> bool:
        """Whether this group has been dissolved and retired."""
        return self._dismissed

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
        result = (
            self.transform if self.parent is None else self.parent.world_transform @ self.transform
        )
        with layout_session() as context:
            for matrix, pivot in self._operations:
                result = matrix.around(context.point(pivot)) @ result
        return result

    @property
    def effective_style(self) -> Style | None:
        return (
            self.style
            if self.style is not None or self.parent is None
            else self.parent.effective_style
        )

    def _description(self) -> Graphic:
        if not self._operations:
            return GroupDescription(self.children, self.transform, self.style)
        from pdl.scene.authoring import Placement

        inverse = Transform() if self.parent is None else self.parent.world_transform.inverse()
        return Placement(Drawing(self.snapshot(), transform=inverse))

    def snapshot(self) -> Placement:
        """Capture world placement and inherited paint without measuring text."""
        from pdl.scene.authoring import Around, Placement, capture

        base = (
            self.transform if self.parent is None else self.parent.world_transform @ self.transform
        )
        result = Placement(Drawing(GroupDescription(self.children, base, self.effective_style)))
        for matrix, pivot in self._operations:
            result = Placement(Drawing(Around(result, matrix, capture(pivot))))
        return result

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
        self.root.automatic_layer = False
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
            member._operations = []
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
            member._operations = []
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
        if self._dismissed:
            raise ValueError("Cannot transform a dismissed Group.")
        if self._operations:
            self._operations.append((transform, (0, 0)))
            return self
        parent = Transform() if self.parent is None else self.parent.world_transform
        self.transform = parent.inverse() @ transform @ parent @ self.transform
        return self

    def translate(self, x: float, y: float) -> Self:
        """Translate by world millimeters."""
        return self.apply_transform(Transform.translate(x, y))

    def rotate(
        self, angle: float, *, about: PointSource | None = None, center: Position | None = None
    ) -> Self:
        """Rotate about a world point, defaulting to the visible group center."""
        self._operations.append((Transform.rotate(angle), self._pivot(about, center)))
        return self

    def scale(
        self,
        x: float,
        y: float | None = None,
        *,
        about: PointSource | None = None,
        center: Position | None = None,
    ) -> Self:
        """Scale about a world point; line widths stay in canvas millimeters."""
        self._operations.append((Transform.scale(x, y), self._pivot(about, center)))
        return self

    def _pivot(self, about: PointSource | None, center: Position | None) -> PointSource:
        if about is not None and center is not None:
            raise TypeError("Specify either about or center, not both.")
        return about if about is not None else center if center is not None else self.anchor()

    def reflect(self, angle: float = 0, *, origin: Position = (0, 0)) -> Self:
        """Reflect about a world line."""
        return self.apply_transform(Transform.reflect(angle, origin))

    def move_to(self, end: PointSource) -> Self:
        """Move the visible group center to an authoring-world target."""
        with layout_session() as context:
            target, current = context.point(end), context.point(self.anchor())
        return self.translate(target.x - current.x, target.y - current.y)

    def place(self, end: PointSource) -> Self:
        return self.move_to(end)

    @property
    def space(self) -> CoordinateSystem:
        from pdl.scene.authoring import InstanceSpace

        return InstanceSpace(self.snapshot())

    def local_snapshot(self) -> Placement:
        from pdl.scene.authoring import Placement

        return Placement(Drawing(self._description()))

    def set_style(self, style: Style) -> Self:
        self.style = style
        return self

    def transformed(self, transform: Transform) -> Placement:
        """Return an independent captured description with an outer transform."""
        from pdl.scene.authoring import Placement

        return Placement(Drawing(self.snapshot(), transform=transform))


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
