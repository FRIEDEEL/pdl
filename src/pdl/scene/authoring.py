"""Mutable authoring handles with isolated captured descriptions."""

from __future__ import annotations

from dataclasses import dataclass, fields, is_dataclass, replace
from typing import Self, cast

from pdl.geometry.bounds import Anchor
from pdl.geometry.primitives import Path, Position
from pdl.geometry.transforms import Transform
from pdl.scene.composition import Drawing, Graphic
from pdl.scene.evaluation import layout_session
from pdl.scene.paint import Style
from pdl.scene.references import AnchorRef, PointSource
from pdl.scene.spaces import WORLD, CoordinateSystem, SpacePoint


def capture[T](value: T) -> T:
    """Capture built-in descriptions, sharing immutable values and frame identities.

    Custom Composite implementations must expose immutable descriptions, as
    required by the decomposition protocol. Built-in mutable paths and Entity
    handles are detached recursively.
    """
    return _capture(value, {})


def _capture[T](value: T, memo: dict[int, object]) -> T:
    if id(value) in memo:
        return cast(T, memo[id(value)])
    memo[id(value)] = value
    if isinstance(value, CoordinateSystem):
        return value
    if isinstance(value, Entity):
        result = value.snapshot()
        memo[id(value)] = result
        return cast(T, result)
    if isinstance(value, Path):
        result = value.to_path()
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
            while isinstance(result.geometry, Placement):
                inner = result.geometry.placed()
                result = Drawing(
                    inner.geometry,
                    result.style if result.style is not None else inner.style,
                    result.transform @ inner.transform,
                )
            return result

    def decompose(self) -> tuple[Drawing, ...]:
        return (self.placed(),)


class Entity:
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
        self._state = Placement(Drawing(capture(geometry), style), space)

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
        return capture(self._state)

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
        self._state = Placement(self._state.drawing, self._state.space, capture(position))
        return self

    def transform(self, transform: Transform) -> Self:
        # Placement-level transforms also transform a previously assigned position.
        """Apply a matrix outside the existing placement in authoring world.

        Args:
            transform: Additional affine transform, including any existing move_to target.

        Returns:
            This modified Entity; the underlying numerical shape is not rewritten.
        """
        self._state = Placement(Drawing(self.snapshot(), transform=transform))
        return self

    def translate(self, x: float, y: float) -> Self:
        """Move by x and y millimeters in authoring world; return this Entity."""
        return self.transform(Transform.translate(x, y))

    def rotate(self, angle: float, *, center: Position = (0, 0)) -> Self:
        """Rotate in degrees about a world point; return this Entity.

        Args:
            angle: Counterclockwise-positive angle in degrees.
            center: World pivot, defaulting to the world origin, not the object center.
        """
        return self.transform(Transform.rotate(angle).around(center))

    def scale(self, x: float, y: float | None = None, *, center: Position = (0, 0)) -> Self:
        """Scale about a world point; return this Entity.

        Args:
            x: Horizontal scale factor.
            y: Vertical scale factor; ``None`` uses x for uniform scaling.
            center: World pivot, defaulting to the world origin.

        Negative factors reflect; zero factors allow degenerate forward geometry.
        Stroke widths remain in Canvas millimeters.
        """
        return self.transform(Transform.scale(x, y).around(center))

    def reflect(self, angle: float = 0, *, origin: Position = (0, 0)) -> Self:
        """Mirror about a world line; return this Entity.

        Args:
            angle: Line direction in counterclockwise-positive degrees from the x axis.
            origin: A world point on the mirror line.
        """
        return self.transform(Transform.reflect(angle, origin))

    def decompose(self) -> tuple[Drawing, ...]:
        return self.snapshot().decompose()


class InstanceSpace(CoordinateSystem):
    """A captured entity frame evaluated only when used."""

    def __init__(self, placement: Placement) -> None:
        super().__init__(name="instance")
        object.__setattr__(self, "placement", placement)

    placement: Placement

    def to_world(self) -> Transform:
        return self.placement.placed().transform
