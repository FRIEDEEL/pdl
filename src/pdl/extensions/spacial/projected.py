"""Editable 2D projection groups with numerically transformed source queries."""

from __future__ import annotations

from typing import Literal

from pdl.author.entity.base import Entity
from pdl.author.entity.group import Group
from pdl.author.geometry.frame import Frame
from pdl.author.geometry.point import Point
from pdl.extensions.spacial.coordinates import Point3D, Vector3D


class ProjectedScene(Group):
    """A projection snapshot, with paint order and fixed camera/source metadata.

    Two-dimensional edits change current coordinates only; the source 3D scene
    is never updated. Source vertices, face centers, and arbitrary projected
    point queries follow the same immediate edits as the visible members.
    Independently projected groups share no visibility buffer or BSP tree.
    """

    def __init__(
        self,
        children: tuple[Entity, ...],
        vertices: tuple[tuple[Point, ...], ...],
        face_centers: tuple[tuple[Point, ...], ...],
        origin: Point3D,
        right: tuple[float, float, float],
        up: tuple[float, float, float],
        distance: float | None = None,
        focal_length: float = 100,
        near: float = 0.1,
        *,
        visibility: Literal["bsp", "centroid", "manual"] = "manual",
        source_faces: tuple[tuple[int, int] | None, ...] = (),
    ) -> None:
        super().__init__(*children)
        self.origin, self.right_basis, self.up_basis = origin, right, up
        self.distance, self.focal_length, self.near = distance, focal_length, near
        self.visibility, self.source_faces = visibility, source_faces
        self._vertices = tuple(tuple(Entity(p) for p in points) for points in vertices)
        self._centers = tuple(tuple(Entity(p) for p in points) for points in face_centers)
        self._projection_frame = Entity(Frame())

    @property
    def children(self) -> tuple[Entity, ...]:
        return self.members

    @staticmethod
    def _points(rows: tuple[tuple[Entity, ...], ...]) -> tuple[tuple[Point, ...], ...]:
        result: list[tuple[Point, ...]] = []
        for row in rows:
            points: list[Point] = []
            for entity in row:
                assert isinstance(entity.geometry, Point)
                points.append(entity.geometry)
            result.append(tuple(points))
        return tuple(result)

    @property
    def vertices(self) -> tuple[tuple[Point, ...], ...]:
        return self._points(self._vertices)

    @property
    def face_centers(self) -> tuple[tuple[Point, ...], ...]:
        return self._points(self._centers)

    def decompose(self) -> tuple[Entity, ...]:
        return self.members

    def reordered(self, order: tuple[int, ...]) -> ProjectedScene:
        if sorted(order) != list(range(len(self.members))):
            raise ValueError("Drawing order must be a permutation of all child indices.")
        result = self.copy()
        result._members = [result.members[i] for i in order]
        result.source_faces = (
            tuple(self.source_faces[i] for i in order) if self.source_faces else ()
        )
        result.visibility = "manual"
        return result

    def point(self, point: Point3D) -> Point:
        offset = point - self.origin
        flat = Point(offset.dot(Vector3D(*self.right_basis)), offset.dot(Vector3D(*self.up_basis)))
        if self.distance is not None:
            toward = Vector3D(*self.right_basis).cross(Vector3D(*self.up_basis))
            axial = self.distance - offset.dot(toward)
            if axial <= self.near:
                raise ValueError("Perspective point must lie beyond the near plane.")
            scale = self.focal_length / axial
            flat = Point(flat.x * scale, flat.y * scale)
        frame = self._projection_frame.geometry
        assert isinstance(frame, Frame)
        return frame.point(flat)

    def vertex(self, object_index: int, vertex_index: int) -> Point:
        return self.vertices[object_index][vertex_index]

    def face_center(self, object_index: int, face_index: int) -> Point:
        return self.face_centers[object_index][face_index]

    def _transform_entities(self) -> tuple[Entity, ...]:
        return (
            *super()._transform_entities(),
            self._projection_frame,
            *(p for row in self._vertices for p in row),
            *(p for row in self._centers for p in row),
        )
