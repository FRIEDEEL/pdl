"""Reproducible convex planar faces, spanning sparse to highly intersecting scenes."""

from colorsys import hsv_to_rgb
from math import cos, pi, sin, sqrt
from random import Random

from pdl import Color
from pdl.extensions.spatial import PerspectiveCamera, Point3D, Vector3D
from playground.visibility.bsp import Face

CAMERA = PerspectiveCamera(azimuth=0, elevation=0, distance=240, focal_length=240)


def world(x: float, y: float, depth: float) -> Point3D:
    """Camera-local screen axes plus axial distance from the eye (larger = farther)."""
    return CAMERA.eye + CAMERA.right * x + CAMERA.up * y + CAMERA.toward_viewer * -depth


def random_faces(count: int, density: float, seed: int) -> tuple[Face, ...]:
    """Sample uniform sphere normals and affine-regular convex 3–7-sided polygons.

    Centers span a fixed 100 mm cube. Density scales radii relative to this cube;
    orientation, aspect ratio, vertex count, rotation and position are randomized.
    Identical seeds/counts use identical draws, so density comparisons are paired.
    """
    rng = Random(seed)
    faces: list[Face] = []
    for index in range(count):
        center = world(rng.uniform(-50, 50), rng.uniform(-50, 50), rng.uniform(190, 290))
        z, azimuth = rng.uniform(-1, 1), rng.uniform(0, 2 * pi)
        normal = Vector3D(sqrt(1 - z * z) * cos(azimuth), sqrt(1 - z * z) * sin(azimuth), z)
        helper = Vector3D(0, 0, 1) if abs(z) < 0.9 else Vector3D(0, 1, 0)
        u = normal.cross(helper).normalized()
        v = normal.cross(u)
        radius = density * 100 * rng.uniform(0.6, 1.2)
        aspect, phase, sides = rng.uniform(0.35, 1), rng.uniform(0, 2 * pi), rng.randint(3, 7)
        points = tuple(
            center
            + u * (radius * cos(phase + i * 2 * pi / sides))
            + v * (radius * aspect * sin(phase + i * 2 * pi / sides))
            for i in range(sides)
        )
        color = Color(*hsv_to_rgb((index * 0.61803398875) % 1, 0.52, 0.88))
        faces.append(Face(points, color, index))
    return tuple(faces)


def crossing() -> tuple[Face, ...]:
    """Two intersecting quadrilaterals exchange front/back at screen x=0."""
    red, blue = Color(0.9, 0.35, 0.24), Color(0.15, 0.57, 0.78)
    return tuple(
        Face(
            tuple(
                world(x, y, 240 + slope * x)
                for x, y in ((-45, -32), (45, -32), (45, 32), (-45, 32))
            ),
            color,
            index,
        )
        for index, (slope, color) in enumerate(((0.7, red), (-0.7, blue)))
    )


def max_trap() -> tuple[Face, ...]:
    """Nonintersecting parallel faces for which farthest-vertex ordering fails."""
    return (
        Face(
            tuple(
                world(x, y, 210 + 0.6 * x) for x, y in ((-45, -25), (60, -25), (60, 25), (-45, 25))
            ),
            Color(0.15, 0.57, 0.78),
            0,
        ),
        Face(
            tuple(
                world(x, y, 218 + 0.6 * x)
                for x, y in ((-42, -20), (-15, -20), (-15, 20), (-42, 20))
            ),
            Color(0.9, 0.35, 0.24),
            1,
        ),
    )


def cycle() -> tuple[Face, ...]:
    """Three disjoint ribbons form a cyclic occlusion at three separate overlaps."""
    corners = ((-42.0, -25.0), (42.0, -25.0), (0.0, 44.0))
    colors = (Color(0.9, 0.35, 0.24), Color(0.15, 0.57, 0.78), Color(0.44, 0.7, 0.3))
    result: list[Face] = []
    for i, a in enumerate(corners):
        b = corners[(i + 1) % 3]
        dx, dy = b[0] - a[0], b[1] - a[1]
        length = sqrt(dx * dx + dy * dy)
        ux, uy = dx / length, dy / length
        vertices: list[Point3D] = []
        for t, offset in ((-0.08, -8), (1.08, -8), (1.08, 8), (-0.08, 8)):
            x, y = a[0] + t * dx - offset * uy, a[1] + t * dy + offset * ux
            # Reciprocal depth is affine in screen space for a 3D plane.
            depth = 1 / ((1 - t) / 210 + t / 260)
            vertices.append(
                world(x * depth / CAMERA.focal_length, y * depth / CAMERA.focal_length, depth)
            )
        result.append(Face(tuple(vertices), colors[i], i))
    return tuple(result)
