"""Independent ray/plane reference versus projected painter-order coverage.

This checks sampled visibility, not an exact proof or pixel-image baseline.
A separate convex point-in-polygon test handles original and fragment coverage.
"""

from dataclasses import dataclass
from math import sqrt
from random import Random

from pdl import PerspectiveCamera, Point, Point3D
from playground.visibility.bsp import Face


def contains(vertices: tuple[Point, ...], point: Point, tolerance: float = 1e-8) -> bool:
    values = tuple(
        (b.x - a.x) * (point.y - a.y) - (b.y - a.y) * (point.x - a.x)
        for a, b in zip(vertices, vertices[1:] + vertices[:1])
    )
    return min(values) >= -tolerance or max(values) <= tolerance


@dataclass(frozen=True)
class Check:
    samples: int
    covered: int
    mismatches: int


def check(
    faces: tuple[Face, ...],
    fragments: tuple[Face, ...],
    camera: PerspectiveCamera,
    samples: int = 2000,
    seed: int = 71,
) -> Check:
    """Compare last painted source with the nearest ray hit at seeded screen points."""
    originals = tuple(
        (face, face.normal, tuple(camera.project(p) for p in face.vertices)) for face in faces
    )
    projected = tuple(
        (face.source, tuple(camera.project(p) for p in face.vertices)) for face in fragments
    )
    rng = Random(seed)
    covered = mismatches = 0
    for index in range(samples):
        if index % 2 and originals:
            # Half the rays target source interiors, so sparse cases are not
            # "validated" mostly by empty background pixels.
            polygon = rng.choice(originals)[2]
            triangle = rng.randrange(1, len(polygon) - 1)
            a, b, c = polygon[0], polygon[triangle], polygon[triangle + 1]
            u, v = sqrt(rng.random()), rng.random()
            point = Point(
                (1 - u) * a.x + u * (1 - v) * b.x + u * v * c.x,
                (1 - u) * a.y + u * (1 - v) * b.y + u * v * c.y,
            )
        else:
            point = Point(rng.uniform(-85, 85), rng.uniform(-85, 85))
        direction = (
            camera.right * (point.x / camera.focal_length)
            + camera.up * (point.y / camera.focal_length)
            + camera.toward_viewer * -1
        )
        hits: list[tuple[float, int]] = []
        for face, normal, polygon in originals:
            if not contains(polygon, point):
                continue
            denominator = normal.dot(direction)
            if abs(denominator) < 1e-12:
                continue
            depth = normal.dot(face.vertices[0] - camera.eye) / denominator
            if depth > camera.near:
                hits.append((depth, face.source))
        nearest = None
        if hits:
            # Match explicit coplanar policy, without resolving near ties arbitrarily.
            best_depth = min(depth for depth, _ in hits)
            nearest = max(source for depth, source in hits if abs(depth - best_depth) < 1e-7)
        painted = None
        for source, polygon in projected:
            if contains(polygon, point):
                painted = source
        covered += nearest is not None
        mismatches += nearest != painted
    return Check(samples, covered, mismatches)


def area(vertices: tuple[Point3D, ...]) -> float:
    """Independent 3D fan area for convex polygons."""
    return sum(
        (vertices[i] - vertices[0]).cross(vertices[i + 1] - vertices[0]).length / 2
        for i in range(1, len(vertices) - 1)
    )
