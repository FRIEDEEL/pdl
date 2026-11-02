"""Projection snapshots preserve source queries under baked 2D transforms."""

import pytest

from pdl import (
    Canvas,
    Group,
    OrthographicCamera,
    PathGeometry,
    Plane3D,
    Point,
    Point3D,
    Scene3D,
    Transform3D,
    line,
    regular_polyhedron,
)
from pdl.author.geometry.shapes import Line as LineGeometry


def test_projection_is_captured_before_source_path_edits() -> None:
    source = PathGeometry().move_to((0, 0)).line_to((1, 0))
    scene = Scene3D((Plane3D().place(source),), visibility="centroid")
    projected = scene.project()
    before = Canvas(30, 30, mode="fit").add(projected).render()
    source.line_to((9, 8))
    assert Canvas(30, 30, mode="fit").add(projected).render() == before
    assert Canvas(30, 30, mode="fit").add(scene.project()).render() != before


def test_projection_metadata_follows_group_transform_without_a_saved_matrix() -> None:
    cube = regular_polyhedron("cube")
    camera = OrthographicCamera(20, 30)
    projected = Scene3D((cube,), camera).project()
    vertex = projected.vertex(0, 3)
    world_point = Point3D(1, 2, 3)
    before = projected.point(world_point)
    group = Group(projected)
    group.translate(20, 30)
    assert projected.vertex(0, 3) == Point(vertex.x + 20, vertex.y + 30)
    assert projected.point(world_point) == Point(before.x + 20, before.y + 30)
    assert projected.face_center(0, 2) == camera.project(cube.face_plane(2).origin) + Point(20, 30)
    assert not hasattr(projected, "transform")
    canvas = Canvas(70, 70, mode="fit").add(group)
    assert "<svg" in canvas.render()
    assert "tikzpicture" in canvas.render("tikz")


def test_face_artwork_coordinates_survive_nonuniform_reflection() -> None:
    cube = regular_polyhedron("cube").with_face_artwork(0, line((0, 0), (1, 2)))
    transform = Transform3D.translate(2, 3, 4) @ Transform3D.scale(-2, 3, 4)
    changed = cube.transformed(transform)
    assert changed.face_artwork is not None
    drawing = changed.face_artwork[0]
    assert drawing is not None
    assert isinstance(drawing.geometry, LineGeometry)
    p = drawing.geometry.end
    assert isinstance(p, Point)
    got = changed.face_plane(0).point(p.x, p.y)
    expected = transform.apply(cube.face_plane(0).point(1, 2))
    assert (got.x, got.y, got.z) == pytest.approx((expected.x, expected.y, expected.z))


def test_reordering_copies_members_and_preserves_source_indices() -> None:
    scene = Scene3D((regular_polyhedron("cube"),)).project()
    changed = scene.reordered(tuple(reversed(range(len(scene.members)))))
    assert changed.source_faces == tuple(reversed(scene.source_faces))
    assert changed.vertices == scene.vertices
    assert changed.face_centers == scene.face_centers
    assert changed.members[0] is not scene.members[-1]
    with pytest.raises(ValueError):
        scene.reordered((0, 0))
