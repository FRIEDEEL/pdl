"""Lighting conventions, camera mapping and backend interoperability."""

import pytest

from pdl import (
    Canvas,
    Circle,
    Color,
    DirectionalLight,
    OrthographicCamera,
    Path,
    Plane3D,
    Point3D,
    Scene3D,
    Style,
    Vector3D,
    regular_polyhedron,
)


def test_lambert_color_mapping() -> None:
    light = DirectionalLight(Vector3D(0, 0, -7), ambient=0.2)
    color = Color(1, 0.5, 0.25)
    assert light.shade(color, Vector3D(0, 0, 3)) == color
    assert light.shade(color, Vector3D(1, 0, 0)) == Color(0.2, 0.1, 0.05)
    assert light.shade(color, Vector3D(0, 0, -1)) == Color(0.2, 0.1, 0.05)
    result = light.shade(color, Vector3D(3, 0, 4))
    assert result.red == pytest.approx(0.84)
    with pytest.raises(ValueError):
        DirectionalLight(Vector3D(0, 0, 0))
    with pytest.raises(ValueError):
        DirectionalLight(ambient=1.1)


def test_camera_and_plane_projection() -> None:
    camera = OrthographicCamera(azimuth=0, elevation=0, target=Point3D(2, 0, 0))
    point = camera.project(Point3D(7, 3, 4))
    assert (point.x, point.y) == pytest.approx((3, 4))
    assert camera.depth(Point3D(7, 3, 4)) == pytest.approx(5)
    plane = Plane3D(Point3D(2, 3, 4), Vector3D(0, 2, 0), Vector3D(0, 0, 1))
    surface = plane.place(Circle((0, 0), 1))
    drawing = Scene3D((surface,), camera=camera, visibility="centroid").decompose()[0]
    from pdl import Point

    projected = drawing.transform.apply(Point(2, 5))
    expected = camera.project(plane.point(2, 5))
    assert (projected.x, projected.y) == pytest.approx((expected.x, expected.y))


def test_global_depth_sort_manual_order_and_capture() -> None:
    near = Plane3D(Point3D(5, 0, 0)).place(Circle((0, 0), 1))
    far = Plane3D(Point3D(-5, 0, 0)).place(Circle((0, 0), 2))
    camera = OrthographicCamera(0, 0)
    scene = Scene3D((near, far), camera, visibility="centroid")
    first = scene.decompose()[0].geometry
    assert isinstance(first, Circle) and first.radius == 2
    first_manual = (
        Scene3D((near, far), camera, sort_faces=False, visibility="centroid")
        .decompose()[0]
        .geometry
    )
    assert isinstance(first_manual, Circle) and first_manual.radius == 1
    path = Path().move_to((0, 0)).line_to((10, 0)).line_to((0, 10)).close()
    canvas = Canvas(50, 50, mode="fit", padding=3)
    canvas.draw(
        Scene3D((Plane3D().place(path, Style(fill=Color(1, 0, 0))),), visibility="centroid")
    )
    before = canvas.render("svg")
    path.line_to((100, 100))
    assert canvas.render("svg") == before


def test_both_vector_backends() -> None:
    canvas = Canvas(50, 50, mode="fit", padding=3)
    canvas.draw(Scene3D((regular_polyhedron("dodecahedron"),)))
    assert "<svg" in canvas.render("svg")
    assert "\\begin{tikzpicture}" in canvas.render("tikz")
