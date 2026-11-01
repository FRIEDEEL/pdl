"""Internal numerical placement state for editable author objects."""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import TYPE_CHECKING, Self

from pdl.author.capture import capture
from pdl.author.composition import Drawing, Graphic
from pdl.author.entity import Entity
from pdl.author.measurement import layout_session
from pdl.author.references import AnchorQuery, PointSource
from pdl.author.spaces import WORLD, CoordinateSystem
from pdl.author.style import Style
from pdl.foundation.geometry.bounds import Anchor
from pdl.foundation.geometry.primitives import Point
from pdl.foundation.geometry.transforms import Transform

if TYPE_CHECKING:
    from pdl.author.composition import Group
    from pdl.author.layers import Layer


def refresh_description(placement: Placement, geometry: Graphic) -> Placement:
    """Refresh local content without changing captured pivots or older draws."""
    content = placement.drawing.geometry
    if isinstance(content, Placement):
        content = refresh_description(content, geometry)
    elif type(content) is type(geometry):
        content = geometry
    return replace(placement, drawing=replace(placement.drawing, geometry=content))


@dataclass(frozen=True)
class Placement:
    """Captured local content and a numerical affine placement."""

    drawing: Drawing
    space: CoordinateSystem = WORLD

    @property
    def paint(self) -> Style | None:
        """Return the explicit paint override."""
        if self.drawing.style is not None:
            return self.drawing.style
        if isinstance(self.drawing.geometry, Placement):
            return self.drawing.geometry.paint
        return None

    def placed(self) -> Drawing:
        result = Drawing(
            self.drawing.geometry,
            self.drawing.style,
            self.space.to_world() @ self.drawing.transform,
        )
        while isinstance(result.geometry, Placement):
            inner = result.geometry.placed()
            result = Drawing(
                inner.geometry,
                result.style if result.style is not None else inner.style,
                result.transform @ inner.transform,
            )
        return result

    def child(self, index: int) -> Drawing:
        """Address a child of a captured group."""
        return Drawing(self).child(index)

    def anchor(self, name: Anchor = "center") -> Point:
        """Immediately measure an anchor of this captured placement."""
        with layout_session(fresh=True) as context:
            return context.point(AnchorQuery(self, name))

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
        # Exposes the instance frame, including its current placement.
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

    def anchor(self, name: Anchor = "center") -> Point:
        """Immediately measure an anchor of the current state.

        Args:
            name: Center or compass anchor, for example ``east`` or ``north west``.

        Returns:
            A numerical point. Later edits do not update it.
            Local shape anchors are transformed with the instance; they need not
            coincide with anchors of the final axis-aligned bounds.
        """
        with layout_session(fresh=True) as context:
            return context.point(AnchorQuery(self.snapshot(), name))

    def move_to(self, position: PointSource) -> Self:
        """Immediately place the current center at a fixed world-space target."""
        with layout_session(fresh=True) as context:
            target = context.point(position)
            center = context.point(AnchorQuery(self.snapshot()))
        return self.transform(Transform.translate(target.x - center.x, target.y - center.y))

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


class DrawingEntity(Entity):
    """Internal editable member for a captured Drawing, including custom composites."""

    def __init__(self, drawing: Drawing) -> None:
        self._entity_state = PlacementState(drawing.geometry, style=drawing.style)
        self._entity_state.placement = Placement(capture(drawing))


class InstanceSpace(CoordinateSystem):
    """A captured entity frame evaluated only when used."""

    def __init__(self, placement: Placement) -> None:
        super().__init__(name="instance")
        object.__setattr__(self, "placement", placement)

    placement: Placement

    def to_world(self) -> Transform:
        return self.placement.placed().transform
