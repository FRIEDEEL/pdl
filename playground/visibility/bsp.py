"""Object-space BSP splitting and perspective projection of opaque convex faces.

All tolerances are in world millimeters. Inputs must be simple, planar, convex
polygons with consistent winding and distinct noncollinear neighboring vertices.
Coplanar ties use source order (later faces cover earlier faces). This prototype
has no curved surfaces, transparency, artwork or near-plane clipping.
"""

from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter

from pdl import Color, Entity, Group, PerspectiveCamera, Point3D, Style, Vector3D, line, polygon
from pdl.extensions.spacial.projected import ProjectedScene
from pdl.extensions.spacial.solids import centroid, face_normal

EPSILON = 1e-8


@dataclass(frozen=True)
class Face:
    """A source face or fragment; edge flags distinguish real edges from cuts."""

    vertices: tuple[Point3D, ...]
    color: Color
    source: int
    edges: tuple[bool, ...] = ()

    @property
    def normal(self) -> Vector3D:
        return face_normal(self.vertices)

    @property
    def boundary(self) -> tuple[bool, ...]:
        return self.edges or (True,) * len(self.vertices)


@dataclass
class Metrics:
    """Work counters and timings, excluding generation, validation and export."""

    input_faces: int = 0
    fragments: int = 0
    splits: int = 0
    classifications: int = 0
    nodes: int = 0
    max_depth: int = 0
    build_seconds: float = 0
    author_seconds: float = 0
    total_seconds: float = 0


@dataclass
class Node:
    """A partition plane, its coplanar faces and two half-space subtrees."""

    origin: Point3D
    normal: Vector3D
    faces: tuple[Face, ...]
    front: Node | None
    back: Node | None


def distances(face: Face, origin: Point3D, normal: Vector3D) -> tuple[float, ...]:
    return tuple((point - origin).dot(normal) for point in face.vertices)


def side(values: tuple[float, ...], epsilon: float) -> int:
    """Return front=1, back=-1, coplanar=0 or straddling=2."""
    front, back = max(values) > epsilon, min(values) < -epsilon
    return 2 if front and back else 1 if front else -1 if back else 0


def split(face: Face, values: tuple[float, ...], epsilon: float) -> tuple[Face, Face]:
    """Clip a convex polygon into two fragments, retaining only original ink edges."""

    def half(sign: int) -> Face:
        # Each appended vertex carries the visibility of the incoming edge.
        points: list[Point3D] = []
        incoming: list[bool] = []
        vertices = face.vertices
        for i, a in enumerate(vertices):
            j = (i + 1) % len(vertices)
            b = vertices[j]
            da = 0.0 if abs(values[i]) <= epsilon else values[i]
            db = 0.0 if abs(values[j]) <= epsilon else values[j]
            inside_a, inside_b = sign * da >= 0, sign * db >= 0
            if inside_a and inside_b:
                points.append(b)
                incoming.append(face.boundary[i])
            elif inside_a != inside_b:
                intersection = a + (b - a) * (da / (da - db))
                points.append(intersection)
                incoming.append(face.boundary[i] if inside_a else False)
                if inside_b:
                    points.append(b)
                    incoming.append(face.boundary[i])
        # Plane-through-vertex cases append duplicate endpoints. Keep the edge
        # flag of the nonzero incoming segment, not the zero-length duplicate.
        clean: list[Point3D] = []
        flags: list[bool] = []
        for point, flag in zip(points, incoming):
            if clean and (point - clean[-1]).length <= epsilon:
                continue
            clean.append(point)
            flags.append(flag)
        if len(clean) > 1 and (clean[0] - clean[-1]).length <= epsilon:
            flags[0] = flags[-1]
            clean.pop()
            flags.pop()
        if len(clean) < 3:
            raise ValueError("Numerically degenerate BSP fragment; rescale geometry/tolerance.")
        return Face(tuple(clean), face.color, face.source, tuple(flags[1:] + flags[:1]))

    return half(1), half(-1)


def build(
    faces: tuple[Face, ...], metrics: Metrics, epsilon: float, fragment_limit: int, depth: int = 0
) -> Node | None:
    """Choose a sampled low-split partition; split every straddling face."""
    if not faces:
        return None
    if depth > 500:
        raise ValueError("BSP depth exceeds prototype safety limit (500).")
    metrics.max_depth = max(metrics.max_depth, depth)
    # Evaluate at most seven candidates, spread through deterministic source order.
    candidates = sorted({i * (len(faces) - 1) // 6 for i in range(7)})
    best = faces[0]
    best_score = float("inf")
    for index in candidates:
        candidate = faces[index]
        origin, normal = candidate.vertices[0], candidate.normal
        counts = {1: 0, -1: 0, 0: 0, 2: 0}
        for face in faces:
            counts[side(distances(face, origin, normal), epsilon)] += 1
            metrics.classifications += 1
        score = 8 * counts[2] + abs(counts[1] - counts[-1])
        if score < best_score:
            best, best_score = candidate, score
    origin, normal = best.vertices[0], best.normal
    front: list[Face] = []
    back: list[Face] = []
    coplanar: list[Face] = []
    for face in faces:
        values = distances(face, origin, normal)
        classification = side(values, epsilon)
        metrics.classifications += 1
        if classification == 2:
            a, b = split(face, values, epsilon)
            front.append(a)
            back.append(b)
            metrics.splits += 1
            if metrics.input_faces + metrics.splits > fragment_limit:
                raise ValueError(f"BSP fragment budget exceeded ({fragment_limit}).")
        elif classification == 1:
            front.append(face)
        elif classification == -1:
            back.append(face)
        else:
            coplanar.append(face)
    metrics.nodes += 1
    return Node(
        origin,
        normal,
        tuple(sorted(coplanar, key=lambda f: f.source)),
        build(tuple(front), metrics, epsilon, fragment_limit, depth + 1),
        build(tuple(back), metrics, epsilon, fragment_limit, depth + 1),
    )


def ordered(node: Node | None, eye: Point3D) -> tuple[Face, ...]:
    """Enumerate far subtree, partition faces, then near subtree."""
    if node is None:
        return ()
    front = (eye - node.origin).dot(node.normal) >= 0
    far, near = (node.back, node.front) if front else (node.front, node.back)
    return ordered(far, eye) + node.faces + ordered(near, eye)


def project(
    faces: tuple[Face, ...],
    camera: PerspectiveCamera,
    *,
    epsilon: float = EPSILON,
    fragment_limit: int = 100_000,
    outlines: bool = True,
) -> tuple[ProjectedScene, Metrics, tuple[Face, ...]]:
    """Build BSP and return ordinary 2D Authoring, timings and source-tagged fragments.

    Timing includes near-plane checks, BSP, traversal, projection and Entity
    construction, but no Canvas evaluation, font measurement, export or oracle.
    Input validity is a caller precondition; duplicate source IDs are rejected.
    """
    started = perf_counter()
    if epsilon <= 0 or fragment_limit < len(faces):
        raise ValueError("Require positive epsilon and sufficient fragment budget.")
    if len({face.source for face in faces}) != len(faces):
        raise ValueError("Source IDs must be unique.")
    # Validate all source points before computing a tree; no silent near clipping.
    vertices = tuple(tuple(camera.project(p) for p in face.vertices) for face in faces)
    centers = tuple((camera.project(centroid(face.vertices)),) for face in faces)
    metrics = Metrics(input_faces=len(faces))
    tree = build(faces, metrics, epsilon, fragment_limit)
    metrics.build_seconds = perf_counter() - started
    author_started = perf_counter()
    fragments = ordered(tree, camera.eye)
    children: list[Entity] = []
    for face in fragments:
        projected = tuple(camera.project(point) for point in face.vertices)
        fill = polygon(projected, style=Style(stroke=None, fill=face.color))
        if outlines:
            edges = tuple(
                line(
                    point,
                    projected[(i + 1) % len(projected)],
                    style=Style(stroke=Color(0.12, 0.16, 0.22), line_width=0.18),
                )
                for i, point in enumerate(projected)
                if face.boundary[i]
            )
            children.append(Group(fill, *edges))
        else:
            children.append(fill)
    right, up = camera.right, camera.up
    author = ProjectedScene(
        tuple(children),
        vertices,
        centers,
        camera.target,
        (right.x, right.y, right.z),
        (up.x, up.y, up.z),
        camera.distance,
        camera.focal_length,
        camera.near,
    )
    metrics.fragments = len(fragments)
    metrics.author_seconds = perf_counter() - author_started
    metrics.total_seconds = perf_counter() - started
    return author, metrics, fragments
