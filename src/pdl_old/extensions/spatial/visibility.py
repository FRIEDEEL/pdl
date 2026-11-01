"""BSP ordering of convex fragments, with original-boundary provenance.

Internal geometry in world millimeters; no camera, typography or backend work.
Finite floating tolerances apply. Supporting planes may split disjoint polygons.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from pdl.extensions.spatial.coordinates import Point3D, Vector3D
from pdl.extensions.spatial.solids import face_normal


@dataclass(frozen=True)
class Fragment:
    """A source face or fragment; edge flags distinguish real edges from cuts."""

    vertices: tuple[Point3D, ...]
    source: int
    edges: tuple[bool, ...] = ()
    normal: Vector3D = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "normal", face_normal(self.vertices))

    @property
    def boundary(self) -> tuple[bool, ...]:
        return self.edges or (True,) * len(self.vertices)


@dataclass
class Metrics:
    """Internal work counters and fragment budget accounting."""

    input_faces: int = 0
    fragments: int = 0
    splits: int = 0
    classifications: int = 0
    nodes: int = 0
    max_depth: int = 0


@dataclass
class Node:
    """A partition plane, its coplanar faces and two half-space subtrees."""

    origin: Point3D
    normal: Vector3D
    faces: tuple[Fragment, ...]
    front: Node | None
    back: Node | None


def distances(face: Fragment, origin: Point3D, normal: Vector3D) -> tuple[float, ...]:
    return tuple((point - origin).dot(normal) for point in face.vertices)


def side(values: tuple[float, ...], epsilon: float) -> int:
    """Return front=1, back=-1, coplanar=0 or straddling=2."""
    front, back = max(values) > epsilon, min(values) < -epsilon
    return 2 if front and back else 1 if front else -1 if back else 0


def split(face: Fragment, values: tuple[float, ...], epsilon: float) -> tuple[Fragment, Fragment]:
    """Clip a convex polygon into two fragments, retaining only original ink edges."""

    def half(sign: int) -> Fragment:
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
        return Fragment(tuple(clean), face.source, tuple(flags[1:] + flags[:1]))

    return half(1), half(-1)


def build(
    faces: tuple[Fragment, ...],
    metrics: Metrics,
    epsilon: float,
    fragment_limit: int,
    depth: int = 0,
) -> Node | None:
    """Choose a sampled low-split partition; split every straddling face."""
    if not faces:
        return None
    if depth > 500:
        raise ValueError("BSP depth exceeds safety limit (500).")
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
    front: list[Fragment] = []
    back: list[Fragment] = []
    coplanar: list[Fragment] = []
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


def ordered(node: Node | None, eye: Point3D | Vector3D) -> tuple[Fragment, ...]:
    """Enumerate far subtree, partition faces, then near subtree."""
    if node is None:
        return ()
    front = ((eye - node.origin) if isinstance(eye, Point3D) else eye).dot(node.normal) >= 0
    far, near = (node.back, node.front) if front else (node.front, node.back)
    return ordered(far, eye) + node.faces + ordered(near, eye)


def convex_fragments(
    vertices: tuple[Point3D, ...], source: int, epsilon: float
) -> tuple[Fragment, ...]:
    """Ear-clip a valid simple planar loop, suppressing triangulation diagonals.

    Convex loops remain intact. Collinear forward vertices are merged before
    triangulation; their combined segment still represents a real boundary.
    """
    normal = face_normal(vertices)
    points = list(vertices)
    changed = True
    while changed and len(points) > 3:
        changed = False
        for i, b in enumerate(points):
            a, c = points[i - 1], points[(i + 1) % len(points)]
            if (b - a).cross(c - b).length <= epsilon * max((b - a).length, (c - b).length):
                points.pop(i)
                changed = True
                break
    vertices = tuple(points)
    count = len(vertices)
    area_epsilon = epsilon * max((p - vertices[0]).length for p in vertices)

    def turn(a: int, b: int, c: int) -> float:
        return (vertices[b] - vertices[a]).cross(vertices[c] - vertices[a]).dot(normal)

    if all(turn(i - 1, i, (i + 1) % count) >= -area_epsilon for i in range(count)):
        return (Fragment(vertices, source),)
    remaining = list(range(count))
    triangles: list[Fragment] = []

    def triangle(indices: tuple[int, int, int]) -> Fragment:
        return Fragment(
            tuple(vertices[i] for i in indices),
            source,
            tuple((indices[(i + 1) % 3] - index) % count == 1 for i, index in enumerate(indices)),
        )

    while len(remaining) > 3:
        for index, b in enumerate(remaining):
            a, c = remaining[index - 1], remaining[(index + 1) % len(remaining)]
            if turn(a, b, c) <= area_epsilon:
                continue
            if any(
                turn(a, b, p) >= -area_epsilon
                and turn(b, c, p) >= -area_epsilon
                and turn(c, a, p) >= -area_epsilon
                for p in remaining
                if p not in (a, b, c)
            ):
                continue
            triangles.append(triangle((a, b, c)))
            remaining.pop(index)
            break
        else:
            raise ValueError(
                "Cannot triangulate face at the BSP tolerance; rescale or reduce tolerance."
            )
    triangles.append(triangle((remaining[0], remaining[1], remaining[2])))
    return tuple(triangles)
