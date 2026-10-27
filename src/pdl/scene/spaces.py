"""Authoring coordinate frames and per-operation world mappings."""

from __future__ import annotations

from contextvars import ContextVar
from dataclasses import dataclass

from pdl.geometry.primitives import Point, Position, Vector
from pdl.geometry.transforms import Transform


@dataclass(frozen=True, eq=False)
class CoordinateSystem:
    """An identity-bearing Cartesian frame relative to its parent.

    Unmapped roots coincide with authoring world coordinates. Canvas mappings
    override a frame's local-to-parent transform for that operation only.
    """

    parent: CoordinateSystem | None = None
    transform: Transform = Transform()
    name: str = "local"

    def __deepcopy__(self, memo: dict[int, object]) -> CoordinateSystem:
        """Frames are immutable identities, shared across captured states."""
        return self

    def child(self, transform: Transform = Transform(), *, name: str = "local") -> CoordinateSystem:
        return CoordinateSystem(self, transform, name)

    def to_world(self) -> Transform:
        local = space_mappings.get().get(self, self.transform)
        return local if self.parent is None else self.parent.to_world() @ local

    def point(self, x: float, y: float) -> SpacePoint:
        return SpacePoint(self, Point(x, y))

    def vector(self, x: float, y: float) -> SpaceVector:
        return SpaceVector(self, Vector(x, y))


WORLD = CoordinateSystem(name="world")
space_mappings: ContextVar[dict[CoordinateSystem, Transform]] = ContextVar("pdl_spaces", default={})


@dataclass(frozen=True)
class SpacePoint:
    """A concrete coordinate expressed in an authoring frame."""

    space: CoordinateSystem
    value: Point

    def resolve(self, target: CoordinateSystem = WORLD) -> Point:
        return (target.to_world().inverse() @ self.space.to_world()).apply(self.value)


@dataclass(frozen=True)
class SpaceVector:
    """A displacement expressed in an authoring frame."""

    space: CoordinateSystem
    value: Vector

    def resolve(self, target: CoordinateSystem = WORLD) -> Vector:
        return (target.to_world().inverse() @ self.space.to_world()).apply_vector(self.value)


def convert_point(value: Position, source: CoordinateSystem, target: CoordinateSystem) -> Point:
    """Convert a numerical point between two authoring frames."""
    return (target.to_world().inverse() @ source.to_world()).apply(value)
