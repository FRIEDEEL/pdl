"""Frozen 2D authoring snapshots produced by explicit 3D projection."""

from __future__ import annotations

from dataclasses import dataclass, replace

from pdl.geometry.bounds import Anchor
from pdl.geometry.primitives import Point
from pdl.scene.composition import Drawing
from pdl.scene.references import AnchorRef
from pdl.spatial.coordinates import Point3D


@dataclass(frozen=True)
class ProjectedScene:
    """A reusable 2D authoring composite, before layout or font measurement.

    children contain projected drawings in paint order. vertices and face_centers
    keep source object/face indices independent of that order; non-polyhedra have
    empty entries. Projected points are fixed local millimeter coordinates, not
    visibility tests or live references. Group the snapshot with its 2D labels
    to move/scale them together. Projection captures built-in mutable artwork;
    changing source paths afterward requires another Scene3D.project call.
    """

    children: tuple[Drawing, ...]
    vertices: tuple[tuple[Point, ...], ...]
    face_centers: tuple[tuple[Point, ...], ...]
    origin: Point3D
    right: tuple[float, float, float]
    up: tuple[float, float, float]

    distance: float | None = None
    focal_length: float = 100
    near: float = 0.1

    def decompose(self) -> tuple[Drawing, ...]:
        """Expose ordinary 2D authoring drawings to the common evaluator."""
        return self.children

    def reordered(self, order: tuple[int, ...]) -> ProjectedScene:
        """Return a snapshot with an explicit back-to-front drawing permutation.

        Indices address current children, not source face indices. With
        Scene3D(sort_faces=False), children follow object order and then face
        order, one child per face (including its artwork) or other object.
        Every child index must occur exactly once. Source point queries stay
        unchanged. This cannot resolve a true cycle without splitting faces.
        """
        if sorted(order) != list(range(len(self.children))):
            raise ValueError("Drawing order must be a permutation of all child indices.")
        return replace(self, children=tuple(self.children[i] for i in order))

    def anchor(self, name: Anchor = "center") -> AnchorRef:
        """Reference the 2D bounds, including layout-dependent face artwork."""
        return AnchorRef(self, name)

    def point(self, point: Point3D) -> Point:
        """Project a world point using this snapshot's fixed camera basis."""
        v = point - self.origin
        flat = Point(
            v.x * self.right[0] + v.y * self.right[1] + v.z * self.right[2],
            v.x * self.up[0] + v.y * self.up[1] + v.z * self.up[2],
        )
        if self.distance is None:
            return flat
        from pdl.spatial.coordinates import Vector3D

        toward = Vector3D(*self.right).cross(Vector3D(*self.up))
        axial = self.distance - v.dot(toward)
        if axial <= self.near:
            raise ValueError("Perspective point must lie beyond the near plane.")
        scale = self.focal_length / axial
        return Point(flat.x * scale, flat.y * scale)

    def vertex(self, object_index: int, vertex_index: int) -> Point:
        """Return a source polyhedron vertex in the snapshot's local 2D space."""
        return self.vertices[object_index][vertex_index]

    def face_center(self, object_index: int, face_index: int) -> Point:
        """Return a projected face vertex-average, whether visible or hidden."""
        return self.face_centers[object_index][face_index]
