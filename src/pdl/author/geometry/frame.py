"""Explicit numerical frames, without ownership or visualization state."""

from __future__ import annotations

from dataclasses import dataclass

from pdl.author.geometry.base import Geometry
from pdl.author.geometry.point import Point, Position, Vector, as_point
from pdl.author.transform.affine import AffineTransform


@dataclass(frozen=True, eq=False)
class Frame(Geometry):
    """An explicit origin and two world-coordinate basis displacements.

    A frame is not attached to ordinary objects. Conversions return fixed
    numerical positions; creating a child bakes its world basis immediately.
    """

    origin: Position = (0, 0)
    x_axis: Vector = Vector(1, 0)
    y_axis: Vector = Vector(0, 1)
    name: str = ""

    def __post_init__(self) -> None:
        as_point(self.origin)

    @property
    def matrix(self) -> AffineTransform:
        p = as_point(self.origin)
        return AffineTransform(self.x_axis.x, self.x_axis.y, self.y_axis.x, self.y_axis.y, p.x, p.y)

    def point(self, position: Position) -> Point:
        return self.matrix.map(position)

    def vector(self, vector: Position | Vector) -> Vector:
        p = vector if isinstance(vector, Vector) else as_point(vector)
        return self.matrix.apply_vector(Vector(p.x, p.y))

    def coordinates(self, position: Position) -> Point:
        return self.matrix.inverse().map(position)

    def child(self, transform: AffineTransform = AffineTransform(), *, name: str = "") -> Frame:
        matrix = self.matrix @ transform
        return Frame(
            matrix.map((0, 0)),
            matrix.apply_vector(Vector(1, 0)),
            matrix.apply_vector(Vector(0, 1)),
            name,
        )

    def to_world(self) -> AffineTransform:
        return self.matrix


WORLD = Frame(name="world")
CoordinateSystem = Frame


@dataclass(frozen=True)
class SpacePoint:
    """A position explicitly expressed in a Frame."""

    space: Frame
    position: Position

    def resolve(self) -> Point:
        return self.space.point(self.position)


@dataclass(frozen=True)
class SpaceVector:
    space: Frame
    vector: Vector

    def resolve(self) -> Vector:
        return self.space.vector(self.vector)
