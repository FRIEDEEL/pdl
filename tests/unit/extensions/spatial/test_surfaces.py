"""Smooth boundaries, washer visibility and independent 2D projection layers."""

import xml.etree.ElementTree as ET
from dataclasses import replace
from math import sqrt
from random import Random

import pytest

from pdl import (
    AnnularCylinder,
    Canvas,
    Color,
    CylinderSurface,
    Drawing,
    OrthographicCamera,
    Path,
    PerspectiveCamera,
    Point,
    Point3D,
    Scene3D,
    Transform3D,
    Vector3D,
    regular_polyhedron,
)
from pdl.author.composition import walk
from pdl.foundation.geometry.primitives import Close, Cubic, Move, Segment


def loops(path: Path) -> list[list[Point]]:
    """Sample emitted Beziers for independent winding checks, without raster tools."""
    result: list[list[Point]] = []
    current = Point(0, 0)
    for command in path.commands:
        if isinstance(command, Move):
            result.append([command.end])
            current = command.end
        elif isinstance(command, Segment):
            result[-1].append(command.end)
            current = command.end
        elif isinstance(command, Cubic):
            a, b, c, d = current, command.control1, command.control2, command.end
            for i in range(1, 49):
                t = i / 48
                weights = ((1 - t) ** 3, 3 * (1 - t) ** 2 * t, 3 * (1 - t) * t * t, t**3)
                result[-1].append(
                    Point(
                        sum(p.x * w for p, w in zip((a, b, c, d), weights)),
                        sum(p.y * w for p, w in zip((a, b, c, d), weights)),
                    )
                )
            current = d
        elif isinstance(command, Close):
            current = result[-1][0]
    return result


def contains(polygons: list[list[Point]], point: Point) -> bool:
    winding = 0
    for polygon in polygons:
        for a, b in zip(polygon, polygon[1:] + polygon[:1]):
            if (a.y > point.y) != (b.y > point.y):
                x = a.x + (point.y - a.y) * (b.x - a.x) / (b.y - a.y)
                if x > point.x:
                    winding += 1 if b.y > a.y else -1
    return winding != 0


@pytest.mark.parametrize("elevation", [-90, -35, 0, 35, 90])
def test_washer_visible_faces_against_independent_ray_intersections(elevation: float) -> None:
    camera = OrthographicCamera(17, elevation)
    washer = AnnularCylinder(outer_radius=10, inner_radius=6, height=8)
    projected = Scene3D((washer,), camera, sort_faces=False).project()
    fills: list[list[list[Point]]] = []
    for leaf in walk((Drawing(projected),)):
        if leaf.style is not None and leaf.style.fill is not None:
            assert isinstance(leaf.geometry, Path)
            fills.append(loops(leaf.geometry))
    # The emitted solid surfaces are inner wall, outer wall, then facing cap.
    ids = [2] if abs(elevation) == 90 else ([0, 1] if elevation == 0 else [0, 1, 2])
    rng = Random(41)
    for _ in range(450):
        screen = Point(rng.uniform(-12, 12), rng.uniform(-12, 16))
        origin = (
            camera.target
            + camera.right * screen.x
            + camera.up * screen.y
            + camera.toward_viewer * 100
        )
        direction = camera.toward_viewer * -1
        hits: list[tuple[float, int]] = []
        a = direction.x**2 + direction.y**2
        b = 2 * (origin.x * direction.x + origin.y * direction.y)
        if a > 1e-12:
            for radius, face in ((6, 0), (10, 1)):
                c = origin.x**2 + origin.y**2 - radius**2
                disc = b * b - 4 * a * c
                if disc > 0:
                    for t in ((-b - sqrt(disc)) / (2 * a), (-b + sqrt(disc)) / (2 * a)):
                        z = origin.z + t * direction.z
                        if 0 < z < 8:
                            hits.append((t, face))
        if abs(direction.z) > 1e-12:
            for z in (0, 8):
                t = (z - origin.z) / direction.z
                x, y = origin.x + t * direction.x, origin.y + t * direction.y
                if 36 < x * x + y * y < 100:
                    hits.append((t, 2))
        expected = min(hits)[1] if hits else None
        actual = None
        for face, polygons in zip(ids, fills, strict=True):
            if contains(polygons, screen):
                actual = face
        assert actual == expected


@pytest.mark.parametrize("sweep", [45, 180, 270, 360])
def test_surface_bezier_boundaries_and_backend_support(sweep: float) -> None:
    surface = CylinderSurface(start_angle=-40, sweep_angle=sweep)
    projected = Scene3D((surface,), sort_faces=False).project()
    assert projected.visibility == "manual"
    assert projected.source_faces == (None,)
    assert projected.vertices == ((),)
    canvas = Canvas(60, 60, mode="fit", padding=3)
    canvas.draw(projected)
    svg = canvas.render("svg")
    root = ET.fromstring(svg)
    assert root.findall(".//{http://www.w3.org/2000/svg}path")
    assert not root.findall(".//{http://www.w3.org/2000/svg}polygon")
    assert not root.findall(".//{http://www.w3.org/2000/svg}image")
    assert " C " in svg
    assert ".. controls" in canvas.render("tikz")


def test_full_surface_has_no_artificial_vertical_seam() -> None:
    surface = CylinderSurface(start_angle=20, sweep_angle=360)
    projected = Scene3D((surface,), OrthographicCamera(0, 30), sort_faces=False).project()
    # Only the two actual silhouette generators receive vertical strokes.
    segments = 0
    for leaf in walk((Drawing(projected),)):
        if leaf.style is not None and leaf.style.stroke is not None:
            assert isinstance(leaf.geometry, Path)
            segments += sum(isinstance(c, Segment) for c in leaf.geometry.commands)
    assert segments == 4  # Each silhouette borders both the far and near branch.


@pytest.mark.parametrize(
    "transform",
    [
        Transform3D.translate(2, 3, 4)
        @ Transform3D.rotate(25, Vector3D(0, 1, 0))
        @ Transform3D.scale(2),
        Transform3D.scale(-2, 2, 2),
    ],
)
def test_surface_similarity_transform_preserves_geometry(transform: Transform3D) -> None:
    surface = CylinderSurface(start_angle=35, sweep_angle=140)
    changed = surface.transformed(transform)
    reflected = transform.x.dot(transform.y.cross(transform.z)) < 0
    for t in (0, 0.3, 1):
        angle = surface.start_angle + t * surface.sweep_angle
        new_angle = -angle if reflected else angle
        actual = changed.point(new_angle, surface.height * 2)
        expected = transform.apply(surface.point(angle, surface.height))
        assert (actual.x, actual.y, actual.z) == pytest.approx((expected.x, expected.y, expected.z))
    assert changed.sweep_angle == surface.sweep_angle
    assert changed.start_angle == (-175 if reflected else 35)


@pytest.mark.parametrize("obj", [CylinderSurface(), AnnularCylinder()])
def test_visibility_modes_and_camera_limits(obj: CylinderSurface | AnnularCylinder) -> None:
    with pytest.warns(UserWarning, match="centroid"):
        assert Scene3D((obj,)).project().visibility == "centroid"
    with pytest.raises(ValueError, match="BSP requires"):
        Scene3D((obj,), visibility="bsp").project()
    with pytest.raises(ValueError, match="OrthographicCamera"):
        Scene3D((obj,), PerspectiveCamera(), sort_faces=False).project()
    for transform in (
        Transform3D.scale(1, 2, 1),
        Transform3D.scale(0),
        Transform3D(y=Vector3D(0.6, 0.8, 0)),
    ):
        with pytest.raises(ValueError):
            obj.transformed(transform)


@pytest.mark.parametrize("value", [0, -1, float("inf"), float("nan")])
def test_invalid_dimensions(value: float) -> None:
    with pytest.raises(ValueError):
        CylinderSurface(radius=value)
    with pytest.raises(ValueError):
        AnnularCylinder(inner_radius=value)
    with pytest.raises(ValueError):
        CylinderSurface(sweep_angle=value)


def test_invalid_frames_angles_and_bore() -> None:
    for axis, radial in (
        (Vector3D(0, 0, 0), Vector3D(1, 0, 0)),
        (Vector3D(0, 0, 1), Vector3D(0, 0, 1)),
    ):
        with pytest.raises(ValueError):
            CylinderSurface(axis=axis, radial=radial)
    with pytest.raises(ValueError):
        CylinderSurface(sweep_angle=361)
    with pytest.raises(ValueError):
        CylinderSurface(start_angle=float("inf"))
    with pytest.raises(ValueError):
        AnnularCylinder(inner_radius=10)


def test_independent_projections_share_coordinates_but_only_canvas_controls_overlap() -> None:
    camera = PerspectiveCamera(15, 25)
    far = regular_polyhedron("cube").transformed(Transform3D.translate(-10, 0, 0))
    near = regular_polyhedron("cube")
    first = Scene3D((near,), camera).project()
    second = Scene3D((far,), camera).project()
    assert first.visibility == second.visibility == "bsp"
    world = Point3D(2, 3, 4)
    assert first.point(world) == second.point(world) == camera.project(world)
    before = first.children
    canvas = Canvas(80, 80, mode="fit")
    canvas.draw(first)
    canvas.draw(second)  # The farther source is intentionally drawn on top.
    flat = list(walk(canvas.drawings))
    assert len(flat) == len(list(walk((Drawing(first),)))) + len(list(walk((Drawing(second),))))
    assert first.children == before
    # Actual SVG paint order follows draw order, not inter-scene world depths.
    red = replace(near, color=Color(1, 0, 0), stroke=None)
    blue = replace(far, color=Color(0, 0, 1), stroke=None)
    canvas = Canvas(80, 80, mode="fit")
    canvas.draw(Scene3D((red,), camera, light=None).project())
    canvas.draw(Scene3D((blue,), camera, light=None).project())
    svg = canvas.render("svg")
    assert svg.rfind('fill="rgb(100%,0%,0%)"') < svg.find('fill="rgb(0%,0%,100%)"')
