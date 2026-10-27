"""Public BSP visibility against independent ray-plane intersections and invariants."""

from dataclasses import replace
from math import cos, pi, sin
from random import Random

import pytest

from pdl import (
    Canvas,
    Color,
    Cylinder,
    OrthographicCamera,
    PerspectiveCamera,
    Plane3D,
    Point,
    Point3D,
    Polygon,
    Polyhedron,
    Scene3D,
    Sphere,
    Text,
    Vector3D,
)
from pdl.scene.composition import walk
from pdl.spatial.solids import face_normal
from pdl.spatial.visibility import convex_fragments

CAMERA = PerspectiveCamera(0, 0, distance=100, focal_length=100)


def screen_point(x: float, y: float, depth: float) -> Point3D:
    return Point3D(100 - depth, x * depth / 100, y * depth / 100)


def crossing() -> tuple[Polyhedron, ...]:
    return tuple(
        Polyhedron(
            tuple(
                screen_point(x, y, 100 + slope * x)
                for x, y in ((-25, -20), (25, -20), (25, 20), (-25, 20))
            ),
            ((0, 1, 2, 3),),
            color=color,
        )
        for slope, color in ((0.6, Color(1, 0, 0)), (-0.6, Color(0, 0, 1)))
    )


def inside(vertices: tuple[Point, ...], point: Point) -> bool:
    """Even-odd ray crossing; independent of BSP's convex clipping implementation."""
    result = False
    for a, b in zip(vertices, vertices[1:] + vertices[:1]):
        if (a.y > point.y) != (b.y > point.y):
            if point.x < a.x + (point.y - a.y) * (b.x - a.x) / (b.y - a.y):
                result = not result
    return result


def assert_visibility(
    objects: tuple[Polyhedron, ...],
    camera: OrthographicCamera,
    samples: int = 1500,
    all_layers: bool = False,
) -> None:
    snapshot = Scene3D(objects, camera, light=None, visibility="bsp").project()
    assert snapshot.visibility == "bsp"
    originals = tuple(
        (i, j, tuple(obj.vertices[k] for k in face))
        for i, obj in enumerate(objects)
        for j, face in enumerate(obj.faces)
    )
    projected: list[tuple[tuple[int, int] | None, tuple[Point, ...]]] = []
    for child, source in zip(snapshot.children, snapshot.source_faces):
        leaves = tuple(walk((child,)))
        geometry = leaves[0].geometry
        assert isinstance(geometry, Polygon)
        projected.append(
            (source, tuple(p if isinstance(p, Point) else Point(*p) for p in geometry.points))
        )
    rng = Random(98)
    covered = 0
    for _ in range(samples):
        point = Point(rng.uniform(-35, 35), rng.uniform(-35, 35))
        if isinstance(camera, PerspectiveCamera):
            origin = camera.eye
            direction = (
                camera.right * (point.x / camera.focal_length)
                + camera.up * (point.y / camera.focal_length)
                + camera.toward_viewer * -1
            )
        else:
            origin = (
                camera.target
                + camera.right * point.x
                + camera.up * point.y
                + camera.toward_viewer * 1000
            )
            direction = camera.toward_viewer * -1
        hits: list[tuple[float, tuple[int, int]]] = []
        for i, j, vertices in originals:
            polygon = tuple(camera.project(p) for p in vertices)
            if not inside(polygon, point):
                continue
            normal = face_normal(vertices)
            denominator = normal.dot(direction)
            if abs(denominator) > 1e-12:
                depth = normal.dot(vertices[0] - origin) / denominator
                hits.append((depth, (i, j)))
        expected = min(hits)[1] if hits else None
        actual = None
        layers: list[tuple[int, int] | None] = []
        for source, polygon in projected:
            if inside(polygon, point):
                actual = source
                layers.append(source)
        if all_layers:
            assert layers == [hit[1] for hit in sorted(hits, key=lambda hit: (-hit[0], hit[1]))]
        covered += expected is not None
        assert actual == expected
    assert covered > 0


@pytest.mark.parametrize("camera", [CAMERA, OrthographicCamera(0, 0)])
def test_intersections_source_mapping_and_backends(camera: OrthographicCamera) -> None:
    objects = crossing()
    scene = Scene3D(objects, camera, light=None)
    snapshot = scene.project()
    assert len(snapshot.children) == 3
    assert set(snapshot.source_faces) == {(0, 0), (1, 0)}
    assert snapshot.vertex(1, 2) == camera.project(objects[1].vertices[2])
    assert_visibility(objects, camera)
    changed = snapshot.reordered(tuple(reversed(range(3))))
    assert changed.visibility == "manual"
    assert changed.source_faces == tuple(reversed(snapshot.source_faces))
    canvas = Canvas(80, 80, mode="fit", padding=3)
    canvas.draw(snapshot)
    assert "<svg" in canvas.render("svg")
    assert "\\begin{tikzpicture}" in canvas.render("tikz")


@pytest.mark.parametrize("seed", [9, 37, 105])
def test_random_rotations_sizes_and_positions(seed: int) -> None:
    rng = Random(seed)
    faces: list[Polyhedron] = []
    for _ in range(18):
        center = Point3D(rng.uniform(-25, 25), rng.uniform(-20, 20), rng.uniform(-20, 20))
        normal = Vector3D(rng.uniform(-1, 1), rng.uniform(-1, 1), rng.uniform(-1, 1)).normalized()
        helper = Vector3D(1, 0, 0) if abs(normal.x) < 0.9 else Vector3D(0, 1, 0)
        u = normal.cross(helper).normalized()
        v = normal.cross(u)
        count = rng.randint(3, 7)
        radius = rng.uniform(8, 24)
        vertices = tuple(
            center
            + u * (radius * cos(i * 2 * pi / count))
            + v * (radius * 0.6 * sin(i * 2 * pi / count))
            for i in range(count)
        )
        faces.append(Polyhedron(vertices, (tuple(range(count)),)))
    assert_visibility(tuple(faces), CAMERA)


def test_concave_loop_area_and_only_real_edges() -> None:
    outline = ((-25, -25), (0, -25), (25, -25), (25, -5), (-5, -5), (-5, 25), (-25, 25))
    vertices = tuple(screen_point(x, y, 100) for x, y in outline)
    obj = Polyhedron(vertices, (tuple(range(len(vertices))),))
    fragments = convex_fragments(vertices, 0, 1e-8)
    # L-shaped area = 50*20 + 20*30; forward collinear vertex is allowed.
    area = sum(
        abs(
            sum(
                (b - a).cross(c - a).dot(face_normal(vertices)) / 2
                for a, b, c in (
                    (f.vertices[0], f.vertices[i], f.vertices[i + 1])
                    for i in range(1, len(f.vertices) - 1)
                )
            )
        )
        for f in fragments
    )
    assert area == pytest.approx(1600)
    perimeter = sum(
        (f.vertices[(i + 1) % len(f.vertices)] - p).length
        for f in fragments
        for i, p in enumerate(f.vertices)
        if f.boundary[i]
    )
    assert perimeter == pytest.approx(200)
    assert_visibility((obj,), CAMERA)
    assert_visibility((replace(obj, vertices=tuple(reversed(vertices))),), CAMERA)


@pytest.mark.parametrize("opacity", [0.25, 1.0])
def test_coplanar_order_winding_and_opacity(opacity: float) -> None:
    a = crossing()[0]
    b = replace(a, vertices=tuple(reversed(a.vertices)), opacity=opacity, color=Color(0, 1, 0))
    snapshot = Scene3D((a, b), CAMERA, light=None).project()
    assert snapshot.source_faces == ((0, 0), (1, 0))
    canvas = Canvas(60, 60, mode="fit")
    canvas.draw(snapshot)
    assert str(opacity) in canvas.render("svg") or opacity == 1


def test_unsupported_modes_and_explicit_fallback() -> None:
    objects = (
        Sphere(),
        Cylinder(),
        Plane3D().place(Text("plane")),
        crossing()[0].with_face_artwork(0, Text("face")),
    )
    for obj in objects:
        with pytest.warns(UserWarning, match="approximate"):
            assert Scene3D((obj,)).project().visibility == "centroid"
        assert Scene3D((obj,), visibility="centroid").project().visibility == "centroid"
        with pytest.raises(ValueError, match="BSP requires"):
            Scene3D((obj,), visibility="bsp").project()
        assert Scene3D((obj,), visibility="bsp", sort_faces=False).project().visibility == "manual"


@pytest.mark.parametrize("tolerance", [0, -1, float("inf"), float("nan")])
def test_invalid_tolerance(tolerance: float) -> None:
    with pytest.raises(ValueError, match="tolerance"):
        Scene3D((), bsp_tolerance=tolerance)


def test_budget_near_plane_and_empty_scene() -> None:
    assert Scene3D(()).project().children == ()
    with pytest.raises(ValueError, match="budget"):
        Scene3D(crossing(), CAMERA, max_fragments=2).project()
    with pytest.raises(ValueError, match="fragment"):
        Scene3D((), max_fragments=0)
    with pytest.raises(ValueError, match="near"):
        Scene3D(
            (
                replace(
                    crossing()[0],
                    vertices=tuple(Point3D(101, p.y, p.z) for p in crossing()[0].vertices),
                ),
            ),
            CAMERA,
        ).project()


def test_disjoint_cycle_visibility() -> None:
    corners = ((-25.0, -15.0), (25.0, -15.0), (0.0, 26.0))
    objects: list[Polyhedron] = []
    for i, a in enumerate(corners):
        b = corners[(i + 1) % 3]
        dx, dy = b[0] - a[0], b[1] - a[1]
        length = (dx * dx + dy * dy) ** 0.5
        vertices: list[Point3D] = []
        for t, offset in ((-0.08, -5), (1.08, -5), (1.08, 5), (-0.08, 5)):
            x, y = a[0] + t * dx - offset * dy / length, a[1] + t * dy + offset * dx / length
            depth = 1 / ((1 - t) / 85 + t / 115)
            vertices.append(screen_point(x, y, depth))
        objects.append(Polyhedron(tuple(vertices), ((0, 1, 2, 3),)))
    assert_visibility(tuple(objects), CAMERA, 3000)


def test_transparent_faces_have_correct_all_layer_order() -> None:
    objects = tuple(replace(obj, opacity=0.4) for obj in crossing())
    assert_visibility(objects, CAMERA, all_layers=True)


def test_projected_strokes_preserve_only_source_boundaries() -> None:
    from pdl import Line
    from pdl.geometry.primitives import point

    objects = crossing()
    snapshot = Scene3D(objects, CAMERA, light=None).project()
    lengths: dict[tuple[int, int], float] = {}
    for child, source in zip(snapshot.children, snapshot.source_faces):
        assert source is not None
        for leaf in walk((child,)):
            if leaf.style is None or leaf.style.stroke is None:
                continue
            geometry = leaf.geometry
            if isinstance(geometry, Line):
                a, b = point(geometry.start), point(geometry.end)
                length = ((a.x - b.x) ** 2 + (a.y - b.y) ** 2) ** 0.5
            else:
                assert isinstance(geometry, Polygon)
                points = tuple(point(p) for p in geometry.points)
                length = sum(
                    ((a.x - b.x) ** 2 + (a.y - b.y) ** 2) ** 0.5
                    for a, b in zip(points, points[1:] + points[:1])
                )
            lengths[source] = lengths.get(source, 0) + length
    for i, obj in enumerate(objects):
        points = tuple(CAMERA.project(p) for p in obj.vertices)
        perimeter = sum(
            ((a.x - b.x) ** 2 + (a.y - b.y) ** 2) ** 0.5
            for a, b in zip(points, points[1:] + points[:1])
        )
        assert lengths[(i, 0)] == pytest.approx(perimeter)
