"""Smooth vector fills, limiting views and light conventions for curved solids."""

import xml.etree.ElementTree as ET

import pytest

from pdl import (
    Canvas,
    Color,
    Cylinder,
    DirectionalLight,
    LinearGradient,
    OrthographicCamera,
    Point3D,
    RadialGradient,
    Scene3D,
    Sphere,
    Vector3D,
)
from pdl.geometry.bounds import geometry_bounds
from pdl.geometry.transforms import placed_geometry
from pdl.scene.composition import GroupDescription


def test_sphere_light_direction_and_backlight() -> None:
    camera = OrthographicCamera(0, 0)
    left = Scene3D((Sphere(),), camera, DirectionalLight(Vector3D(-1, 1, 0)), visibility="centroid")
    right = Scene3D(
        (Sphere(),), camera, DirectionalLight(Vector3D(-1, -1, 0)), visibility="centroid"
    )
    left_fill = left.decompose()[0].style
    right_fill = right.decompose()[0].style
    assert left_fill is not None and right_fill is not None
    assert isinstance(left_fill.fill, RadialGradient)
    assert isinstance(right_fill.fill, RadialGradient)
    assert isinstance(left_fill.fill.center, tuple) and isinstance(right_fill.fill.center, tuple)
    assert left_fill.fill.center[0] < 0.5 < right_fill.fill.center[0]
    assert left_fill.fill.stops == right_fill.fill.stops
    color = Color(1, 0.5, 0.25)
    back = Scene3D(
        (Sphere(color=color),),
        camera,
        DirectionalLight(Vector3D(1, 0, 0), 0.2),
        visibility="centroid",
    )
    style = back.decompose()[0].style
    assert style is not None and isinstance(style.fill, RadialGradient)
    assert all(stop.color == Color(0.2, 0.1, 0.05) for stop in style.fill.stops)


def test_cylinder_side_colors_sample_lambert_and_cap_normal() -> None:
    camera = OrthographicCamera(0, 30)
    light = DirectionalLight(Vector3D(-1, 0, -1))
    cylinder = Cylinder(color=Color(1, 0.5, 0.25))
    drawing = Scene3D((cylinder,), camera, light, visibility="centroid").decompose()[0]
    assert isinstance(drawing.geometry, GroupDescription)
    side, cap = drawing.geometry.children
    assert side.style is not None and isinstance(side.style.fill, LinearGradient)
    stops = side.style.fill.stops
    assert stops[0].offset == 0 and stops[-1].offset == 1
    assert stops[0].color == light.shade(cylinder.color, Vector3D(0, -1, 0))
    assert stops[16].color == light.shade(cylinder.color, Vector3D(1, 0, 0))
    assert cap.style is not None
    assert cap.style.fill == light.shade(cylinder.color, Vector3D(0, 0, 1))


@pytest.mark.parametrize("elevation", [-90, -35, 0, 35, 90])
def test_limiting_camera_views_and_native_gradients(elevation: float) -> None:
    cylinder = Cylinder(base=Point3D(3, 4, 5), radius=5, height=20)
    canvas = Canvas(70, 70, mode="fit", padding=5)
    canvas.draw(
        Scene3D(
            (cylinder, Sphere(Point3D(25, 0, 0), radius=5)),
            camera=OrthographicCamera(0, elevation),
            visibility="centroid",
        )
    )
    svg = canvas.render("svg")
    root = ET.fromstring(svg)
    ns = {"s": "http://www.w3.org/2000/svg"}
    assert len(root.findall(".//s:radialGradient", ns)) == 1
    assert len(root.findall(".//s:linearGradient", ns)) == (0 if abs(elevation) == 90 else 1)
    assert not root.findall(".//s:polygon", ns)
    assert not root.findall(".//s:image", ns)
    assert "\\pgfdeclarefunctionalshading" in canvas.render("tikz")


def test_unlit_and_axis_magnitude() -> None:
    sphere = Sphere(radius=8)
    cylinder = Cylinder(axis=Vector3D(0, 0, 17))
    normalized = Cylinder()
    first_canvas, second_canvas = Canvas(60, 60), Canvas(60, 60)
    first_canvas.draw(Scene3D((cylinder,), visibility="centroid"))
    second_canvas.draw(Scene3D((normalized,), visibility="centroid"))
    assert first_canvas.render("svg") == second_canvas.render("svg")
    scene = Scene3D((sphere, cylinder), light=None, visibility="centroid")
    first = scene.decompose()[0]
    assert first.style is not None and first.style.fill == sphere.color
    canvas = Canvas(60, 60, mode="fit")
    canvas.draw(scene)
    assert "Gradient" not in canvas.render("svg")
    projected = Scene3D((sphere,), light=None, visibility="centroid").decompose()[0]
    from pdl import Circle

    assert isinstance(projected.geometry, Circle)
    box = geometry_bounds(placed_geometry(projected.geometry, projected.transform))
    assert box.width == pytest.approx(16)
    assert box.height == pytest.approx(16)


@pytest.mark.parametrize("size", [0, -1, float("nan"), float("inf")])
def test_invalid_sizes(size: float) -> None:
    with pytest.raises(ValueError):
        Sphere(radius=size)
    with pytest.raises(ValueError):
        Cylinder(height=size)
    with pytest.raises(ValueError):
        Cylinder(radius=size)


def test_zero_axis_is_rejected() -> None:
    with pytest.raises(ValueError):
        Cylinder(axis=Vector3D(0, 0, 0))
