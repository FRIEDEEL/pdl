"""Shared mutable authoring operations, independent of geometry implementations."""

from __future__ import annotations

from copy import deepcopy
from typing import TYPE_CHECKING, Self

if TYPE_CHECKING:
    from pdl.author.composition import Group
    from pdl.author.frames import Frame
    from pdl.author.layers import Layer
    from pdl.author.placement import Placement, PlacementState
    from pdl.author.references import PointSource
    from pdl.author.spaces import CoordinateSystem
    from pdl.author.style import Style
    from pdl.foundation.geometry.bounds import Anchor
    from pdl.foundation.geometry.primitives import Path, Point, Position
    from pdl.foundation.geometry.transforms import Transform


class Entity:
    """Base for editable drawing and reference objects.

    Geometry parameters describe local content. Authoring methods mutate placement
    and return this object; ``copy`` creates an independent editable object.
    ``Canvas.draw`` captures state, so subsequent edits affect future draws only.
    Stroke widths stay in canvas millimeters under scaling.

    Construct concrete drawing or reference objects; this base is not a wrapper.
    """

    _entity_state: PlacementState
    _reference_frame: Frame
    description_only: bool = False
    automatic_layer: bool = False

    def __init__(self) -> None:
        if type(self) is Entity:
            raise TypeError("Entity is a base class; construct a concrete drawing object.")

    def to_path(self) -> Path:
        """Require concrete geometry to supply its path representation."""
        raise TypeError("This entity has no direct path; capture it before lowering.")

    def _state(self) -> PlacementState:
        from pdl.author.capture import description
        from pdl.author.composition import Drawing
        from pdl.author.placement import Placement, PlacementState

        self.description_only = False
        if "_entity_state" not in self.__dict__:
            state = PlacementState.__new__(PlacementState)
            state.parent = None
            state.assigned_layer = 0
            state.placement = Placement(Drawing(description(self)))
            self._entity_state = state
        else:
            from pdl.author.placement import refresh_description

            self._entity_state.placement = refresh_description(
                self._entity_state.placement, description(self)
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
        from pdl.author.frames import Frame

        if "_reference_frame" not in self.__dict__:
            self._reference_frame = Frame()
        return self._reference_frame

    @frame.setter
    def frame(self, value: Frame) -> None:
        """Assign an explicit operation frame without changing object placement."""
        self._reference_frame = value

    @property
    def space(self) -> CoordinateSystem:
        """Capture the current placed coordinate frame."""
        return self._state().space

    def in_space(self, space: CoordinateSystem) -> Self:
        """Interpret this placement in an explicit authoring coordinate system.

        This changes coordinate placement; it does not assign the independent
        operation reference exposed by ``frame``. Canvas mappings may override it.
        """
        from dataclasses import replace

        self.placement = replace(self.placement, space=space)
        return self

    def snapshot(self) -> Placement:
        return self._state().snapshot()

    def local_snapshot(self) -> Placement:
        return self._state().local_snapshot()

    def set_layer(self, layer: int | Layer) -> Self:
        from pdl.author.layers import assign_layer

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

    def anchor(self, name: Anchor = "center") -> Point:
        """Immediately measure a fixed world point of the current object state."""
        from pdl.author.measurement import layout_session
        from pdl.author.references import AnchorQuery

        with layout_session(fresh=True) as context:
            return context.point(AnchorQuery(self.snapshot(), name))

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
        from pdl.foundation.geometry.transforms import Transform

        return self.apply_transform(Transform.translate(x, y))

    def rotate(
        self,
        angle: float,
        *,
        about: PointSource | None = None,
    ) -> Self:
        """Rotate in degrees around an explicit world pivot or the object center.

        A missing pivot immediately measures the current object center, including
        text when necessary.
        """
        return self._around("rotate", angle, None, about)

    def scale(
        self,
        x: float,
        y: float | None = None,
        *,
        about: PointSource | None = None,
    ) -> Self:
        """Scale around an explicit world pivot or the current measured object center."""
        return self._around("scale", x, y, about)

    def _around(
        self,
        operation: str,
        x: float,
        y: float | None,
        about: PointSource | None,
    ) -> Self:
        from pdl.author.measurement import layout_session
        from pdl.foundation.geometry.transforms import Transform

        with layout_session(fresh=True) as context:
            pivot = context.point(about) if about is not None else self.anchor()
        matrix = Transform.rotate(x) if operation == "rotate" else Transform.scale(x, y)
        return self.apply_transform(matrix.around(pivot))

    def reflect(self, angle: float = 0, *, origin: Position = (0, 0)) -> Self:
        """Reflect about a world-space line."""
        from pdl.foundation.geometry.transforms import Transform

        return self.apply_transform(Transform.reflect(angle, origin))

    def copy(self) -> Self:
        """Copy independently, detaching a grouped object without moving it.

        Group copies include independent members. External immutable
        CoordinateSystem identities retain their existing mapping semantics.
        """
        result = deepcopy(self)
        result.description_only = False
        if self.parent is not None:
            from pdl.author.composition import Drawing
            from pdl.author.placement import Placement

            state = deepcopy(self.snapshot())
            result.parent = None
            result.placement = Placement(Drawing(state))
            result.assigned_layer = self.layer
            result.automatic_layer = self.root.automatic_layer
        return result
