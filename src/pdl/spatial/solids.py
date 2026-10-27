"""Finite plane placements and indexed polygonal solids."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations, product
from math import atan2, isfinite, sqrt
from typing import Literal

from pdl.scene.composition import Drawing, Graphic
from pdl.scene.paint import BLACK, Color, Style
from pdl.spatial.coordinates import Point3D, Transform3D, Vector3D


def centroid(points: tuple[Point3D, ...]) -> Point3D:
    count = len(points)
    return Point3D(
        sum(p.x for p in points) / count,
        sum(p.y for p in points) / count,
        sum(p.z for p in points) / count,
    )


def face_normal(points: tuple[Point3D, ...]) -> Vector3D:
    """Return the oriented unit normal using a translation-independent area sum."""
    total = Vector3D(0, 0, 0)
    for i in range(1, len(points) - 1):
        total = total + (points[i] - points[0]).cross(points[i + 1] - points[0])
    return total.normalized()


@dataclass(frozen=True)
class Plane3D:
    """A 2D chart embedded in 3D: origin + x*u + y*v.

    u and v are independent dimensionless basis vectors; they need not be
    orthogonal or unit length. The normal follows u cross v. The infinite
    plane is not drawn; place finite 2D graphics on it with ``place``.
    """

    origin: Point3D = Point3D(0, 0, 0)
    u: Vector3D = Vector3D(1, 0, 0)
    v: Vector3D = Vector3D(0, 1, 0)

    def __post_init__(self) -> None:
        self.u.cross(self.v).normalized()

    @property
    def normal(self) -> Vector3D:
        return self.u.cross(self.v).normalized()

    def point(self, x: float, y: float) -> Point3D:
        return self.origin + self.u * x + self.v * y

    def transformed(self, transform: Transform3D) -> Plane3D:
        return Plane3D(
            transform.apply(self.origin),
            transform.apply_vector(self.u),
            transform.apply_vector(self.v),
        )

    def place(
        self,
        graphic: Graphic,
        style: Style | None = None,
        *,
        depth_point: tuple[float, float] = (0, 0),
    ) -> Surface3D:
        """Place a 2D drawing; depth_point is its local sorting reference.

        The default reference is the plane origin. For overlapping surfaces,
        supply the local center. A surface is sorted as one item, not split.
        Canvas.draw captures mutable built-in graphics inside the placement.
        Surface paint is not lit automatically; use DirectionalLight.shade
        with this plane's world normal to choose a fill explicitly.
        """
        return Surface3D(self, Drawing(graphic, style), self.point(*depth_point))


@dataclass(frozen=True)
class Surface3D:
    """A finite drawing in a plane, with an explicit world sorting reference."""

    plane: Plane3D
    drawing: Drawing
    depth_point: Point3D


@dataclass(frozen=True)
class Polyhedron:
    """An indexed solid with simple convex planar polygon faces.

    Vertices are in millimeters. Face indices wind counterclockwise viewed
    from outside; supplied winding is preserved and determines lighting.
    Intersections, manifold topology and whole-solid convexity are not checked.
    Faces must be convex and nondegenerate. Face colors override color by index.
    Transforms return a new solid; normals are recomputed from transformed faces.
    """

    vertices: tuple[Point3D, ...]
    faces: tuple[tuple[int, ...], ...]
    color: Color = Color(0.35, 0.65, 0.9)
    face_colors: tuple[Color, ...] | None = None
    stroke: Color | None = BLACK
    line_width: float = 0.25

    def __post_init__(self) -> None:
        if not self.vertices or not self.faces:
            raise ValueError("A polyhedron needs vertices and faces.")
        Style(stroke=self.stroke, line_width=self.line_width)
        if self.face_colors is not None and len(self.face_colors) != len(self.faces):
            raise ValueError("Provide exactly one color per face.")
        for face in self.faces:
            if len(face) < 3 or len(set(face)) != len(face):
                raise ValueError("Faces need at least three distinct indices.")
            if any(i < 0 or i >= len(self.vertices) for i in face):
                raise ValueError("Face index is outside the vertex array.")
            points = tuple(self.vertices[i] for i in face)
            normal = face_normal(points)
            size = max((p - points[0]).length for p in points)
            tolerance = 1e-9 * size
            if any(abs((p - points[0]).dot(normal)) > tolerance for p in points):
                raise ValueError("Face vertices must be coplanar.")
            # Every vertex must lie on the inner side of every directed edge.
            for a, b in zip(points, points[1:] + points[:1]):
                if any((b - a).cross(p - a).dot(normal) < -tolerance * size for p in points):
                    raise ValueError("Faces must be convex and consistently ordered.")

    def transformed(self, transform: Transform3D) -> Polyhedron:
        """Apply an affine transform, preserving outward winding under reflection."""
        determinant = transform.x.dot(transform.y.cross(transform.z))
        faces = tuple(tuple(reversed(f)) for f in self.faces) if determinant < 0 else self.faces
        return Polyhedron(
            tuple(transform.apply(p) for p in self.vertices),
            faces,
            self.color,
            self.face_colors,
            self.stroke,
            self.line_width,
        )


type PlatonicKind = Literal["tetrahedron", "cube", "octahedron", "dodecahedron", "icosahedron"]


def _convex_faces(vertices: tuple[Point3D, ...]) -> tuple[tuple[int, ...], ...]:
    """Find supporting planes of the small, centered regular-solid vertex sets."""
    found: dict[tuple[int, ...], tuple[int, ...]] = {}
    for i, j, k in combinations(range(len(vertices)), 3):
        cross = (vertices[j] - vertices[i]).cross(vertices[k] - vertices[i])
        if cross.length < 1e-9:
            continue
        normal = cross.normalized()
        distances = tuple((p - vertices[i]).dot(normal) for p in vertices)
        if min(distances) < -1e-8 and max(distances) > 1e-8:
            continue
        indices = tuple(n for n, d in enumerate(distances) if abs(d) < 1e-8)
        if indices in found:
            continue
        center = centroid(tuple(vertices[n] for n in indices))
        if normal.dot(center - Point3D(0, 0, 0)) < 0:
            normal = normal * -1
        u = (vertices[indices[0]] - center).normalized()
        v = normal.cross(u)
        found[indices] = tuple(
            sorted(
                indices,
                key=lambda n: atan2((vertices[n] - center).dot(v), (vertices[n] - center).dot(u)),
            )
        )
    return tuple(found.values())


def regular_polyhedron(
    kind: PlatonicKind, radius: float = 10, color: Color = Color(0.35, 0.65, 0.9)
) -> Polyhedron:
    """Construct one of all five Platonic solids centered at the origin.

    Args:
        kind: English solid name (cube is the regular hexahedron).
        radius: Positive circumradius in millimeters, identical for all kinds.
        color: Intrinsic RGB color before directional lighting.

    No numerical or hull dependency is required; supporting planes are found
    from these small fixed vertex sets, merging coplanar triangles into faces.
    """
    if not isfinite(radius) or radius <= 0:
        raise ValueError("Radius must be finite and positive.")
    phi = (1 + sqrt(5)) / 2
    triples: list[tuple[float, float, float]] = []
    if kind == "tetrahedron":
        triples = [(1, 1, 1), (1, -1, -1), (-1, 1, -1), (-1, -1, 1)]
    elif kind == "cube":
        triples = [(x, y, z) for x, y, z in product((-1.0, 1.0), repeat=3)]
    elif kind == "octahedron":
        triples = [(s, 0.0, 0.0) for s in (-1.0, 1.0)] + [(0.0, s, 0.0) for s in (-1.0, 1.0)]
        triples += [(0, 0, s) for s in (-1, 1)]
    elif kind in ("icosahedron", "dodecahedron"):
        a, b = (1.0, phi) if kind == "icosahedron" else (1 / phi, phi)
        for s, t in product((-1, 1), repeat=2):
            triples.extend(((0, s * a, t * b), (t * b, 0, s * a), (s * a, t * b, 0)))
        if kind == "dodecahedron":
            triples.extend((x, y, z) for x, y, z in product((-1.0, 1.0), repeat=3))
    else:
        raise ValueError(f"Unknown Platonic solid: {kind}")
    raw = tuple(Point3D(*p) for p in triples)
    faces = _convex_faces(raw)
    factor = radius / (raw[0] - Point3D(0, 0, 0)).length
    return Polyhedron(
        tuple(Point3D(p.x * factor, p.y * factor, p.z * factor) for p in raw), faces, color
    )
