"""Explicit authoring snapshots, source correspondence and face-local artwork."""

import xml.etree.ElementTree as ET
from dataclasses import replace

import pytest

from pdl import (
    Canvas,
    Color,
    Drawing,
    Group,
    Line,
    Node,
    OrthographicCamera,
    Path,
    Point3D,
    Scene3D,
    Style,
    Text,
    Transform,
    Transform3D,
    regular_polyhedron,
)
from pdl.scene.composition import GroupDescription


def test_projection_is_a_captured_2d_authoring_snapshot() -> None:
    source = Path().move_to((0, 0)).line_to((1, 0))
    from pdl import Plane3D

    scene = Scene3D((Plane3D().place(source),))
    projected = scene.project()
    canvas = Canvas(30, 30, mode="fit")
    canvas.draw(projected)
    before = canvas.render("svg")
    source.line_to((9, 8))
    canvas_again = Canvas(30, 30, mode="fit")
    canvas_again.draw(projected)
    assert canvas_again.render("svg") == before
    changed = Canvas(30, 30, mode="fit")
    changed.draw(scene.project())
    assert changed.render("svg") != before


def test_source_indices_survive_painter_sorting_and_2d_composition() -> None:
    cube = regular_polyhedron("cube")
    camera = OrthographicCamera(20, 30)
    projected = Scene3D((cube,), camera).project()
    assert projected.vertex(0, 3) == camera.project(cube.vertices[3])
    assert projected.point(Point3D(1, 2, 3)) == camera.project(Point3D(1, 2, 3))
    plane = cube.face_plane(2)
    assert projected.face_center(0, 2) == camera.project(plane.origin)
    marker = Line(projected.vertex(0, 0), projected.face_center(0, 2))
    component = Group((Drawing(projected), Drawing(marker)))
    canvas = Canvas(70, 70, mode="fit")
    canvas.draw(Drawing(component, transform=Transform.translate(20, 20) @ Transform.rotate(10)))
    assert "<svg" in canvas.render("svg")
    assert "\\begin{tikzpicture}" in canvas.render("tikz")
    # A different camera produces a new snapshot without changing the first.
    assert (
        replace(Scene3D((cube,), camera), camera=OrthographicCamera(80, 30)).project().vertices
        != projected.vertices
    )


def test_artwork_is_grouped_with_face_without_font_measurement() -> None:
    cube = regular_polyhedron("cube")
    for i in range(len(cube.faces)):
        cube = cube.with_face_artwork(i, Node(Text("A"), style=Style(stroke=None)))
    projected = Scene3D((cube,)).project()  # no font discovery or Node measurement here
    groups = [d.geometry for d in projected.children if isinstance(d.geometry, GroupDescription)]
    assert len(groups) == 6
    assert all(len(g.children) == 2 for g in groups)
    canvas = Canvas(60, 60, mode="fit", padding=4)
    canvas.draw(projected)
    root = ET.fromstring(canvas.render("svg"))
    assert len(root.findall(".//{http://www.w3.org/2000/svg}text")) == 6
    assert "transform shape" in canvas.render("tikz")


def test_face_artwork_frame_survives_nonuniform_reflection() -> None:
    cube = regular_polyhedron("cube").with_face_artwork(0, Line((0, 0), (1, 2)))
    transform = Transform3D.translate(2, 3, 4) @ Transform3D.scale(-2, 3, 4)
    changed = cube.transformed(transform)
    assert changed.face_artwork is not None
    drawing = changed.face_artwork[0]
    assert drawing is not None
    from pdl import Point

    local = drawing.transform.apply(Point(1, 2))
    got = changed.face_plane(0).point(local.x, local.y)
    expected = transform.apply(cube.face_plane(0).point(1, 2))
    assert (got.x, got.y, got.z) == pytest.approx((expected.x, expected.y, expected.z))


def test_invalid_face_artwork_index_and_count() -> None:
    cube = regular_polyhedron("cube")
    with pytest.raises(IndexError):
        cube.with_face_artwork(6, Text("wrong"))
    with pytest.raises(ValueError):
        replace(cube, face_artwork=(Drawing(Line((0, 0), (1, 0)), Style(fill=Color(1, 0, 0))),))
