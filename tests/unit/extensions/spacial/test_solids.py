"""Topology, regularity and orientation of all Platonic solids."""

from collections import Counter

import pytest

from pdl import Color, Plane3D, Point3D, Polyhedron, Transform3D, Vector3D, regular_polyhedron
from pdl.extensions.spacial.solids import PlatonicKind, centroid, face_normal


@pytest.mark.parametrize(
    ("kind", "vertices", "edges", "faces", "sides"),
    [
        ("tetrahedron", 4, 6, 4, 3),
        ("cube", 8, 12, 6, 4),
        ("octahedron", 6, 12, 8, 3),
        ("dodecahedron", 20, 30, 12, 5),
        ("icosahedron", 12, 30, 20, 3),
    ],
)
def test_platonic_topology_and_regularity(
    kind: PlatonicKind, vertices: int, edges: int, faces: int, sides: int
) -> None:
    solid = regular_polyhedron(kind, radius=17)
    assert len(solid.vertices) == vertices
    assert len(solid.faces) == faces
    incidence: Counter[tuple[int, int]] = Counter()
    angles: list[float] = []
    for face in solid.faces:
        assert len(face) == sides
        points = tuple(solid.vertices[i] for i in face)
        assert face_normal(points).dot(centroid(points) - Point3D(0, 0, 0)) > 0
        for i, a in enumerate(face):
            b = face[(i + 1) % sides]
            incidence[(min(a, b), max(a, b))] += 1
            previous = solid.vertices[face[i - 1]] - solid.vertices[a]
            following = solid.vertices[b] - solid.vertices[a]
            angles.append(previous.normalized().dot(following.normalized()))
    assert len(incidence) == edges
    assert set(incidence.values()) == {2}
    lengths = [(solid.vertices[a] - solid.vertices[b]).length for a, b in incidence]
    assert lengths == pytest.approx([lengths[0]] * edges)
    assert angles == pytest.approx([angles[0]] * len(angles))
    assert [(p - Point3D(0, 0, 0)).length for p in solid.vertices] == pytest.approx([17] * vertices)
    assert vertices - edges + faces == 2


def test_reflection_preserves_outward_normals() -> None:
    solid = regular_polyhedron("cube").transformed(Transform3D.scale(-2, 1, 3))
    for face in solid.faces:
        points = tuple(solid.vertices[i] for i in face)
        assert face_normal(points).dot(centroid(points) - Point3D(0, 0, 0)) > 0


def test_invalid_faces_and_planes() -> None:
    points = (Point3D(0, 0, 0), Point3D(1, 0, 0), Point3D(0, 1, 0), Point3D(0, 0, 1))
    for face in ((0, 1), (0, 1, 7), (0, 1, 1), (0, 1, 2, 3)):
        with pytest.raises(ValueError):
            Polyhedron(points, (face,))
    with pytest.raises(ValueError):
        Plane3D(u=Vector3D(1, 0, 0), v=Vector3D(2, 0, 0))
    with pytest.raises(ValueError):
        regular_polyhedron("cube", radius=-1)
    with pytest.raises(ValueError):
        Polyhedron(points, ((0, 1, 2),), face_colors=(Color(1, 0, 0), Color(0, 0, 1)))


def test_concave_planar_face_is_valid_but_crossing_loop_is_not() -> None:
    points = tuple(Point3D(x, y, 0) for x, y in ((0, 0), (3, 0), (3, 1), (1, 1), (1, 3), (0, 3)))
    solid = Polyhedron(points, ((0, 1, 2, 3, 4, 5),))
    assert len(solid.faces[0]) == 6
    with pytest.raises(ValueError, match="self-intersect"):
        Polyhedron(points, ((0, 2, 5, 1, 4),))
    repeated = (*points, Point3D(0, 0, 0))
    with pytest.raises(ValueError):
        Polyhedron(repeated, ((0, 6, 1, 2),))
