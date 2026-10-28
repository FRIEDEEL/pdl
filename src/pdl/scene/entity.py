"""Shared mutable authoring operations, independent of geometry implementations."""

from __future__ import annotations

from copy import deepcopy
from typing import TYPE_CHECKING, Self

if TYPE_CHECKING:
    from pdl.geometry.bounds import Anchor
    from pdl.geometry.primitives import Path, Position
    from pdl.geometry.transforms import Transform
    from pdl.scene.authoring import Placement, PlacementState
    from pdl.scene.composition import Graphic, Group
    from pdl.scene.frames import Frame
    from pdl.scene.layers import Layer
    from pdl.scene.paint import Style
    from pdl.scene.references import AnchorRef, PointSource
    from pdl.scene.spaces import CoordinateSystem


class Entity:
    """Base for editable drawing and reference objects.

    Geometry parameters describe local content. Authoring methods mutate placement
    and return this object; ``copy`` creates an independent editable object.
    ``Canvas.draw`` captures state, so subsequent edits affect future draws only.
    Stroke widths stay in canvas millimeters under scaling.

    Direct ``Entity(geometry)`` construction remains a compatibility adapter;
    prefer operating on Circle, Line, Text and other concrete objects directly.
    """

    _entity_state: PlacementState
    _reference_frame: Frame
    description_only: bool = False
    automatic_layer: bool = False

    def __init__(
        self,
        geometry: Graphic,
        *,
        style: Style | None = None,
        space: CoordinateSystem | None = None,
    ) -> None:
        from pdl.scene.authoring import PlacementState
        from pdl.scene.spaces import WORLD

        self._entity_state = PlacementState(geometry, style=style, space=space or WORLD)

    def to_path(self) -> Path:
        """Require concrete geometry to supply its path representation."""
        raise TypeError("This entity has no direct path; capture it before lowering.")

    def _state(self) -> PlacementState:
        from pdl.scene.authoring import Placement, PlacementState, description
        from pdl.scene.composition import Drawing

        self.description_only = False
        if "_entity_state" not in self.__dict__:
            state = PlacementState.__new__(PlacementState)
            state.parent = None
            state.assigned_layer = 0
            state.placement = Placement(Drawing(description(self)))
            self._entity_state = state
        else:
            from pdl.scene.authoring import refresh_description

            self._entity_state.placement = (
                refresh_description(self._entity_state.placement, description(self))
                if type(self) is not Entity
                else self._entity_state.placement
            )
        return self._entity_state

    @property
    def parent(self) -> Group | None:
        """Return the containing Group; ordinary entities cannot own children."""
        return self._state().parent

    @parent.setter
    def parent(self, value: Group | None) -> None:
        self._state().parent = value

    @property
    def placement(self) -> Placement:
        """Return the internal captured placement description."""
        return self._state().placement

    @placement.setter
    def placement(self, value: Placement) -> None:
        self._state().placement = value

    @property
    def assigned_layer(self) -> int | Layer:
        return self._state().assigned_layer

    @assigned_layer.setter
    def assigned_layer(self, value: int | Layer) -> None:
        self._state().assigned_layer = value

    @property
    def root(self) -> Entity | Group:
        return self if self.parent is None else self.parent.root

    @property
    def layer(self) -> int | Layer:
        return self.root.assigned_layer

    @property
    def frame(self) -> Frame:
        """Return an independent world-aligned operation frame.

        The frame does not follow object transformations. Include it explicitly
        in a Gather or Group when a shared transformation is desired.
        """
        from pdl.scene.frames import Frame

        if "_reference_frame" not in self.__dict__:
            self._reference_frame = Frame()
        return self._reference_frame

    @frame.setter
    def frame(self, value: Frame) -> None:
        """Assign an explicit operation frame without changing object placement."""
        self._reference_frame = value

    @property
    def space(self) -> CoordinateSystem:
        """Capture the current placed frame for legacy coordinate APIs."""
        return self._state().space

    def snapshot(self) -> Placement:
        return self._state().snapshot()

    def local_snapshot(self) -> Placement:
        return self._state().local_snapshot()

    def set_layer(self, layer: int | Layer) -> Self:
        from pdl.scene.layers import assign_layer

        assign_layer(self, layer)
        self.root.automatic_layer = False
        return self

    def set_style(self, style: Style) -> Self:
        """Assign an instance-wide style override without changing geometry."""
        from dataclasses import replace

        self.placement = replace(
            self.placement, drawing=replace(self.placement.drawing, style=style)
        )
        return self

    def anchor(self, name: Anchor = "center") -> AnchorRef:
        """Capture a deferred anchor of the current placement."""
        return self._state().anchor(name)

    def move_to(self, end: PointSource) -> Self:
        """Place the transformed bounds center at a target; mutate this object."""
        self._state().move_to(end)
        return self

    def place(self, end: PointSource) -> Self:
        """Place the bounds center; unlike Path.move_to this never builds a path."""
        self._state().move_to(end)
        return self

    def apply_transform(self, transform: Transform) -> Self:
        """Apply a world-space affine matrix; leave the reference frame unchanged."""
        self._state().transform(transform)
        return self

    def translate(self, x: float, y: float) -> Self:
        """Translate by world-space millimeters."""
        from pdl.geometry.transforms import Transform

        return self.apply_transform(Transform.translate(x, y))

    def rotate(
        self,
        angle: float,
        *,
        about: PointSource | None = None,
        center: Position | None = None,
    ) -> Self:
        """Rotate in degrees around an explicit world pivot or the object center.

        ``center`` is a compatibility alias. A missing pivot is captured as a
        deferred center anchor, so text measurement is not required here.
        """
        return self._around("rotate", angle, None, about, center)

    def scale(
        self,
        x: float,
        y: float | None = None,
        *,
        about: PointSource | None = None,
        center: Position | None = None,
    ) -> Self:
        """Scale around an explicit world pivot or the deferred object center."""
        return self._around("scale", x, y, about, center)

    def _around(
        self,
        operation: str,
        x: float,
        y: float | None,
        about: PointSource | None,
        center: Position | None,
    ) -> Self:
        from pdl.geometry.transforms import Transform
        from pdl.scene.authoring import Around, Placement, capture
        from pdl.scene.composition import Drawing

        if about is not None and center is not None:
            raise TypeError("Specify either about or center, not both.")
        pivot = about if about is not None else center
        # Preserve the historical world-origin default of the compatibility wrapper.
        if pivot is None:
            pivot = (0, 0) if type(self) is Entity else self.anchor()
        matrix = Transform.rotate(x) if operation == "rotate" else Transform.scale(x, y)
        state = self.snapshot()
        parent = self.parent
        inverse = Transform() if parent is None else parent.world_transform.inverse()
        self.placement = Placement(
            Drawing(Around(state, matrix, capture(pivot)), transform=inverse)
        )
        return self

    def reflect(self, angle: float = 0, *, origin: Position = (0, 0)) -> Self:
        """Reflect about a world-space line."""
        from pdl.geometry.transforms import Transform

        return self.apply_transform(Transform.reflect(angle, origin))

    def copy(self) -> Self:
        """Copy independently, detaching a grouped object without moving it.

        Group copies include independent members. External immutable legacy
        CoordinateSystem identities retain their existing mapping semantics.
        """
        result = deepcopy(self)
        result.description_only = False
        if self.parent is not None:
            from pdl.scene.authoring import Placement
            from pdl.scene.composition import Drawing

            state = deepcopy(self.snapshot())
            result.parent = None
            result.placement = Placement(Drawing(state))
            result.assigned_layer = self.layer
            result.automatic_layer = self.root.automatic_layer
        return result
