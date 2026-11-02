"""Pinhole mapping, deferred plane outlines and approximate painter semantics."""

import xml.etree.ElementTree as ET
from dataclasses import replace
from math import hypot
from pathlib import Path as FilePath

import pytest

from pdl import (
    Canvas,
    Color,
    Group,
    Node,
    PerspectiveCamera,
    Plane3D,
    Point,
    Point3D,
    Scene3D,
    Sphere,
    Style,
    Translation,
    Vector3D,
    regular_polyhedron,
    text,
)
from pdl import (
    PathGeometry as Path,
)
from pdl.author.geometry.path import Move, Segment
from pdl.extensions.spacial._author import make_entity as Drawing
from pdl.extensions.spacial.planar import PerspectiveArtwork


def test_pinhole_scale_and_snapshot_point_queries() -> None:
    camera = PerspectiveCamera(0, 0, distance=100, focal_length=50)
    assert camera.eye == Point3D(100, 0, 0)
    assert camera.project(Point3D(0, 10, 4)) == Point(5, 2)
    assert camera.project(Point3D(50, 10, 4)) == Point(10, 4)
    cube = regular_polyhedron("cube")
    snapshot = Scene3D((cube,), camera).project()
    for i, p in enumerate(cube.vertices):
        assert snapshot.vertex(0, i) == camera.project(p)
        assert snapshot.point(p) == camera.project(p)
    for i in range(len(cube.faces)):
        assert snapshot.face_center(0, i) == camera.project(cube.face_plane(i).origin)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"distance": 0},
        {"focal_length": -1},
        {"near": 100},
        {"distance": float("inf")},
        {"near": float("nan")},
    ],
)
def test_invalid_camera_distances(kwargs: dict[str, float]) -> None:
    with pytest.raises(ValueError):
        PerspectiveCamera(
            distance=kwargs.get("distance", 100),
            focal_length=kwargs.get("focal_length", 100),
            near=kwargs.get("near", 0.1),
        )


def test_near_plane_rejection_in_geometry_queries_and_artwork() -> None:
    camera = PerspectiveCamera(0, 0, distance=10, near=1)
    for p in (Point3D(9, 0, 0), Point3D(12, 0, 0)):
        with pytest.raises(ValueError, match="near"):
            camera.project(p)
        with pytest.raises(ValueError, match="near"):
            Scene3D((), camera, visibility="centroid").project().point(p)
    with pytest.raises(ValueError, match="near"):
        Scene3D((regular_polyhedron("cube", radius=30),), camera, visibility="centroid").project()
    surface = Plane3D(Point3D(9, 0, 0), Vector3D(0, 1, 0), Vector3D(0, 0, 1))
    canvas = Canvas(40, 40)
    with pytest.raises(ValueError, match="near"):
        canvas.draw(
            Scene3D(
                (surface.place(Path().move_to((0, 0)).line_to((1, 1))),),
                camera,
                visibility="centroid",
            ).project()
        )


def test_depth_sort_is_axial_and_manual_order_overrides_it() -> None:
    camera = PerspectiveCamera(0, 0)
    # The near plane's reference is farther away in Euclidean distance.
    near = Plane3D(Point3D(20, 200, 0)).place(Path().move_to((0, 0)).line_to((1, 0)))
    far = Plane3D(Point3D(-20, 0, 0)).place(Path().move_to((0, 0)).line_to((1, 0)))
    automatic = Scene3D((near, far), camera, visibility="centroid").project()
    manual = Scene3D((near, far), camera, sort_faces=False, visibility="centroid").project()
    assert automatic.children[0].bounds.bottom == pytest.approx(0)
    assert manual.children[0].bounds.bottom == pytest.approx(0)
    assert automatic.children[0].bounds.left == pytest.approx(0)
    assert manual.children[0].bounds.left == pytest.approx(250)


def test_transparent_faces_keep_back_faces_and_back_artwork() -> None:
    cube = replace(regular_polyhedron("cube"), opacity=0.3)
    for i in range(len(cube.faces)):
        cube = cube.with_face_artwork(i, text(str(i)))
    canvas = Canvas(70, 70, mode="fit", padding=4)
    canvas.draw(Scene3D((cube,), PerspectiveCamera(), visibility="centroid").project())
    root = ET.fromstring(canvas.render("svg"))
    # Six faces plus six outlined numbers; native 2D legends remain native text.
    paths = root.findall(".//{http://www.w3.org/2000/svg}path")
    assert len(paths) == 12
    assert sum(p.get("opacity") == "0.3" for p in paths) == 6
    assert "\\begin{tikzpicture}" in canvas.render("tikz")
    with pytest.raises(ValueError):
        replace(cube, opacity=1.1)


def test_deferred_text_outlines_capture_and_native_legend() -> None:
    source = Path().move_to((-10, 0)).line_to((10, 0))
    artwork = Group(Drawing(source), Drawing(Node(text("Plane"), style=Style(stroke=None))))
    plane = Plane3D(Point3D(0, 0, 0), Vector3D(1, 1, 0), Vector3D(0, 0, 1))
    snapshot = Scene3D(
        (plane.place(artwork),), PerspectiveCamera(0, 0), visibility="centroid"
    ).project()
    baseline = Canvas(60, 60, mode="fit")
    baseline.draw(snapshot)
    before = baseline.render("svg")
    source.line_to((30, 20))
    canvas = Canvas(60, 60, mode="fit")
    canvas.draw(snapshot)
    canvas.draw(text("Legend", position=(0, 15)), Style(stroke=None, fill=Color(0, 0, 0)))
    svg = canvas.render("svg")
    assert "Plane" not in svg
    assert "Legend" in svg
    fresh = Canvas(60, 60, mode="fit")
    fresh.draw(snapshot)
    assert fresh.render("svg") == before


def test_projected_curve_has_bounded_deviation() -> None:
    camera = PerspectiveCamera(0, 0, distance=50, focal_length=50)
    plane = Plane3D(u=Vector3D(1, 1, 0), v=Vector3D(0, 0, 1))
    path = Path().move_to((0, 0)).quadratic_to((20, 20), (30, 0))
    placement = Translation(1, 2)
    leaf = PerspectiveArtwork(plane, Drawing(path, transform=placement), camera).decompose()[0]
    assert isinstance(leaf.geometry, Path)
    vertices = [c.end for c in leaf.geometry.commands if isinstance(c, (Move, Segment))]
    for i in range(101):
        t = i / 100
        local = placement.map(Point(40 * t * (1 - t) + 30 * t * t, 40 * t * (1 - t)))
        expected = camera.project(plane.point(local.x, local.y))
        distances: list[float] = []
        for a, b in zip(vertices, vertices[1:]):
            dx, dy = b.x - a.x, b.y - a.y
            u = max(
                0, min(1, ((expected.x - a.x) * dx + (expected.y - a.y) * dy) / (dx * dx + dy * dy))
            )
            distances.append(hypot(expected.x - a.x - u * dx, expected.y - a.y - u * dy))
        assert min(distances) <= 0.020001


def test_unsupported_curved_solid_is_explicit() -> None:
    with pytest.raises(ValueError, match="OrthographicCamera"):
        Scene3D((Sphere(),), PerspectiveCamera(), visibility="centroid").project()


def test_reordering_preserves_source_queries_and_validates_permutation() -> None:
    cube = regular_polyhedron("cube")
    snapshot = Scene3D((cube,), PerspectiveCamera(), sort_faces=False).project()
    order = tuple(reversed(range(len(snapshot.children))))
    changed = snapshot.reordered(order)
    assert [d.bounds for d in changed.children] == [d.bounds for d in reversed(snapshot.children)]
    assert changed.vertex(0, 2) == snapshot.vertex(0, 2)
    assert changed.face_center(0, 2) == snapshot.face_center(0, 2)
    for invalid in ((0, 0), (0,), tuple(range(1, 7))):
        with pytest.raises(ValueError, match="permutation"):
            snapshot.reordered(invalid)


def test_perspective_images_are_rejected_instead_of_drawing_their_bounds() -> None:
    from pdl import image

    asset = FilePath(__file__).parents[4] / "examples/tutorial/media/quadrants.png"
    surface = Plane3D().place(image(asset, 10, 10))
    canvas = Canvas(30, 30)
    with pytest.raises(ValueError, match="embedded images"):
        canvas.draw(Scene3D((surface,), PerspectiveCamera(), visibility="centroid").project())
