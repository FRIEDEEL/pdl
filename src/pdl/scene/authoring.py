"""Mutable authoring handles with isolated captured descriptions."""

from __future__ import annotations

from contextvars import ContextVar
from dataclasses import dataclass, fields, is_dataclass, replace
from typing import TYPE_CHECKING, Self, cast

if TYPE_CHECKING:
    from pdl.scene.composition import Group
    from pdl.scene.layers import Layer

from pdl.geometry.bounds import Anchor
from pdl.geometry.primitives import Path
from pdl.geometry.transforms import Transform
from pdl.scene.composition import Drawing, Graphic
from pdl.scene.entity import Entity
from pdl.scene.evaluation import layout_session
from pdl.scene.paint import Style
from pdl.scene.references import AnchorRef, PointSource
from pdl.scene.spaces import WORLD, CoordinateSystem, SpacePoint


def description[T](value: T) -> T:
    """Copy local geometry parameters without mutable authoring state."""
    from copy import copy

    result = value.to_path() if isinstance(value, Path) else copy(value)
    if isinstance(result, Entity):
        result.__dict__.pop("_entity_state", None)
        result.__dict__.pop("_reference_frame", None)
        result.description_only = True
    return cast(T, result)


def refresh_description(placement: Placement, geometry: Graphic) -> Placement:
    """Refresh local content without changing captured pivots or older draws."""
    content = placement.drawing.geometry
    if isinstance(content, Placement):
        content = refresh_description(content, geometry)
    elif isinstance(content, Around):
        if isinstance(content.content, Placement):
            content = replace(content, content=refresh_description(content.content, geometry))
    elif type(content) is type(geometry):
        content = geometry
    return replace(placement, drawing=replace(placement.drawing, geometry=content))


_capture_owners: ContextVar[list[object]] = ContextVar("pdl_capture_owners", default=[])
_capture_memo: ContextVar[dict[int, object] | None] = ContextVar("pdl_capture", default=None)


def capture[T](value: T) -> T:
    """Capture built-in descriptions, sharing immutable values and frame identities.

    Custom Composite implementations must expose immutable descriptions, as
    required by the decomposition protocol. Built-in mutable paths and Entity
    handles are detached recursively.
    """
    current = _capture_memo.get()
    if current is not None:
        return _capture(value, current)
    memo: dict[int, object] = {}
    token = _capture_memo.set(memo)
    owners_token = _capture_owners.set([])
    try:
        return _capture(value, memo)
    finally:
        _capture_memo.reset(token)
        _capture_owners.reset(owners_token)


def _capture[T](value: T, memo: dict[int, object]) -> T:
    # Refreshing authoring descriptions creates temporary objects; retain their
    # owners throughout capture so Python cannot reuse a memoized identity.
    _capture_owners.get().append(value)
    if id(value) in memo:
        return cast(T, memo[id(value)])
    memo[id(value)] = value
    from pdl.scene.frames import FrameSpace

    if isinstance(value, FrameSpace):
        result = CoordinateSystem(transform=value.to_world(), name=value.name)
        memo[id(value)] = result
        return cast(T, result)
    if isinstance(value, CoordinateSystem):
        return value
    from pdl.components.flowchart import FlowNode
    from pdl.scene.composition import Group

    if isinstance(value, FlowNode):
        return cast(T, value.snapshot())
    if isinstance(value, Group):
        return cast(T, value.snapshot())
    if (
        isinstance(value, Entity)
        and not value.description_only
        and (type(value) is Entity or "_entity_state" in value.__dict__)
    ):
        result = value.snapshot()
        memo[id(value)] = result
        return cast(T, result)
    if isinstance(value, Path):
        result = value.to_path()
        result.description_only = True
        memo[id(value)] = result
        return cast(T, result)
    if isinstance(value, tuple):
        items = tuple(_capture(item, memo) for item in cast(tuple[object, ...], value))
        result = (
            cast(tuple[object, ...], value)
            if all(a is b for a, b in zip(cast(tuple[object, ...], value), items, strict=True))
            else items
        )
        memo[id(cast(object, value))] = result
        return cast(T, result)
    if is_dataclass(value) and not isinstance(value, type):
        changes: dict[str, object] = {}
        for field in fields(value):
            if field.init:
                original: object = getattr(value, field.name)
                copied = _capture(original, memo)
                if copied is not original:
                    changes[field.name] = copied
        if isinstance(value, Entity):
            from copy import copy

            result = copy(value)
            for name, copied in changes.items():
                setattr(result, name, copied)
            result.description_only = True
        else:
            result = replace(value, **changes) if changes else value
        memo[id(value)] = result
        return cast(T, result)
    return value


@dataclass(frozen=True)
class Placement:
    """A captured instance before its position dependency is evaluated."""

    drawing: Drawing
    space: CoordinateSystem = WORLD
    position: PointSource | None = None

    @property
    def paint(self) -> Style | None:
        """Return explicit paint without evaluating placement dependencies."""
        if self.drawing.style is not None:
            return self.drawing.style
        if isinstance(self.drawing.geometry, Placement):
            return self.drawing.geometry.paint
        return None

    def placed(self) -> Drawing:
        with layout_session() as context:
            transform = self.drawing.transform
            if self.position is not None:
                # Positions are world-authoring references; unqualified pairs
                # belong to the placement's parent frame.
                if isinstance(self.position, (AnchorRef, SpacePoint)):
                    world = context.point(self.position)
                    p = self.space.to_world().inverse().apply(world)
                else:
                    p = context.point(self.position)
                origin = context.point(
                    AnchorRef(Drawing(self.drawing.geometry, transform=transform))
                )
                transform = Transform.translate(p.x - origin.x, p.y - origin.y) @ transform
            result = Drawing(
                self.drawing.geometry, self.drawing.style, self.space.to_world() @ transform
            )
            while isinstance(result.geometry, (Placement, Around)):
                inner = (
                    result.geometry.placed()
                    if isinstance(result.geometry, Placement)
                    else result.geometry.decompose()[0]
                )
                result = Drawing(
                    inner.geometry,
                    result.style if result.style is not None else inner.style,
                    result.transform @ inner.transform,
                )
            return result

    def child(self, index: int) -> Drawing:
        """Address a child of a captured group."""
        return Drawing(self).child(index)

    def anchor(self, name: Anchor = "center") -> AnchorRef:
        """Return a deferred reference to this captured description."""
        return AnchorRef(self, name)

    def transformed(self, transform: Transform) -> Placement:
        """Return a captured description with an outer world-space matrix."""
        return Placement(Drawing(self, transform=transform))

    def decompose(self) -> tuple[Drawing, ...]:
        return (self.placed(),)


class PlacementState:
    """A mutable handle for placing geometry and assigning instance paint.

    Args:
        geometry: Reusable shape or composite; built-in mutable state is captured.
        style: Optional instance style.
        space: Parent authoring frame; ordinary move_to pairs use this frame.

    Placement methods mutate this handle and return it for chaining. Anchor,
    space, and draw captures never follow later edits. Move a Group when an
    assembly should transform as a whole.
    """

    def __init__(
        self, geometry: Graphic, *, style: Style | None = None, space: CoordinateSystem = WORLD
    ) -> None:
        self.parent: Group | None = None
        self.assigned_layer: int | Layer = 0
        self.placement = Placement(Drawing(capture(geometry), style), space)

    @property
    def space(self) -> CoordinateSystem:
        # Exposes the instance frame, including deferred placement.
        """Capture this instance's local frame without measuring its geometry.

        The frame origin comes from the original geometry, not its bounds center.
        Later edits to the Entity do not update this captured frame.
        """
        return InstanceSpace(self.snapshot())

    def snapshot(self) -> Placement:
        """Return the current placement description, without fixing font metrics."""
        state = self.local_snapshot()
        if self.parent is None:
            return state
        return Placement(
            Drawing(
                state,
                state.paint if state.paint is not None else self.parent.effective_style,
                self.parent.world_transform,
            )
        )

    def local_snapshot(self) -> Placement:
        return capture(self.placement)

    @property
    def root(self) -> PlacementState | Group:
        """Return the outermost selectable instance."""
        return self if self.parent is None else self.parent.root

    @property
    def layer(self) -> int | Layer:
        """Return the effective layer of this instance or its outermost Group."""
        return self.root.assigned_layer

    def anchor(self, name: Anchor = "center") -> AnchorRef:
        """Capture an anchor of the current state for later evaluation.

        Args:
            name: Center or compass anchor, for example ``east`` or ``north west``.

        Returns:
            A deferred reference. Later edits to this Entity do not update it.
            Local shape anchors are transformed with the instance; they need not
            coincide with anchors of the final axis-aligned bounds.
        """
        return AnchorRef(self.snapshot(), name)

    def move_to(self, position: PointSource) -> Self:
        """Place the transformed local bounds center at a target.

        Args:
            position: Pair in the parent frame, explicit SpacePoint, or AnchorRef.

        Returns:
            This modified Entity. Position/font dependencies remain unevaluated.
        """
        if self.parent is not None:
            target = Placement(Drawing(self.snapshot()), position=capture(position))
            self.placement = Placement(
                Drawing(target, transform=self.parent.world_transform.inverse())
            )
            return self
        self.placement = Placement(self.placement.drawing, self.placement.space, position)
        return self

    def transform(self, transform: Transform) -> Self:
        # Placement-level transforms also transform a previously assigned position.
        """Apply a matrix outside the existing placement in authoring world.

        Args:
            transform: Additional affine transform, including any existing move_to target.

        Returns:
            This modified Entity; the underlying numerical shape is not rewritten.
        """
        parent = Transform() if self.parent is None else self.parent.world_transform
        local = parent.inverse() @ transform @ parent
        self.placement = Placement(Drawing(self.local_snapshot(), transform=local))
        return self


@dataclass(frozen=True)
class Around:
    """A captured affine operation with a deferred world-space pivot."""

    content: Graphic
    matrix: Transform
    pivot: PointSource

    def decompose(self) -> tuple[Drawing, ...]:
        with layout_session() as context:
            return (Drawing(self.content, transform=self.matrix.around(context.point(self.pivot))),)


class InstanceSpace(CoordinateSystem):
    """A captured entity frame evaluated only when used."""

    def __init__(self, placement: Placement) -> None:
        super().__init__(name="instance")
        object.__setattr__(self, "placement", placement)

    placement: Placement

    def to_world(self) -> Transform:
        return self.placement.placed().transform
