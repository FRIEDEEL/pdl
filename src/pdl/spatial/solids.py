"""Finite plane placements and indexed polygonal solids."""

from __future__ import annotations

from dataclasses import dataclass, replace
from itertools import combinations, product
from math import atan2, isfinite, sqrt
from typing import Literal

from pdl.geometry.transforms import Transform
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


def _validate_simple_loop(points: tuple[Point3D, ...], normal: Vector3D, tolerance: float) -> None:
    """Reject zero-length edges, retracing corners and nonadjacent crossings."""
    size = max((p - points[0]).length for p in points)
    area_tolerance = tolerance * size
    count = len(points)
    for i, a in enumerate(points):
        b = points[(i + 1) % count]
        if (b - a).length <= tolerance:
            raise ValueError("Face edges must have nonzero length.")
        previous = points[i - 1] - a
        following = b - a
        if previous.cross(following).length <= area_tolerance and previous.dot(following) > 0:
            raise ValueError("Face edges must not retrace a corner.")
        for j in range(i + 1, count):
            if j == i + 1 or (i == 0 and j == count - 1):
                continue
            c, d = points[j], points[(j + 1) % count]
            # Oriented half-plane tests plus bounding boxes handle touching
            # and collinear overlap as well as proper crossings.
            ab_c = (b - a).cross(c - a).dot(normal)
            ab_d = (b - a).cross(d - a).dot(normal)
            cd_a = (d - c).cross(a - c).dot(normal)
            cd_b = (d - c).cross(b - c).dot(normal)
            opposite_ab = min(ab_c, ab_d) <= area_tolerance and max(ab_c, ab_d) >= -area_tolerance
            opposite_cd = min(cd_a, cd_b) <= area_tolerance and max(cd_a, cd_b) >= -area_tolerance
            overlaps = all(
                max(min(x1, x2), min(x3, x4)) <= min(max(x1, x2), max(x3, x4)) + tolerance
                for x1, x2, x3, x4 in (
                    (a.x, b.x, c.x, d.x),
                    (a.y, b.y, c.y, d.y),
                    (a.z, b.z, c.z, d.z),
                )
            )
            if opposite_ab and opposite_cd and overlaps:
                raise ValueError("Face loops must not self-intersect or touch themselves.")


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
    """An indexed polyhedron with simple planar polygon face loops.

    Vertices are in millimeters. Face indices wind counterclockwise viewed
    from outside; supplied winding is preserved and determines lighting.
    Inter-face intersections, manifold topology and whole-solid convexity are
    not checked. Faces may be concave, but must be simple and nondegenerate.
    Holes are not supported. Face colors override color by index.
    opacity (default 1) applies independently to each face fill and stroke;
    attached artwork retains its own style and opacity. Back faces are retained.
    Transforms return a new solid; normals are recomputed from transformed faces.
    """

    vertices: tuple[Point3D, ...]
    faces: tuple[tuple[int, ...], ...]
    color: Color = Color(0.35, 0.65, 0.9)
    face_colors: tuple[Color, ...] | None = None
    stroke: Color | None = BLACK
    line_width: float = 0.25
    face_artwork: tuple[Drawing | None, ...] | None = None
    opacity: float = 1

    def __post_init__(self) -> None:
        if not self.vertices or not self.faces:
            raise ValueError("A polyhedron needs vertices and faces.")
        Style(stroke=self.stroke, line_width=self.line_width, opacity=self.opacity)
        if self.face_colors is not None and len(self.face_colors) != len(self.faces):
            raise ValueError("Provide exactly one color per face.")
        if self.face_artwork is not None and len(self.face_artwork) != len(self.faces):
            raise ValueError("Provide exactly one artwork entry per face.")
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
            _validate_simple_loop(points, normal, tolerance)

    def face_plane(self, index: int) -> Plane3D:
        """Return a centered unit chart for a face, with v toward world +z.

        The origin is the vertex average, not the area centroid. Projected +z
        gives the local up direction; horizontal faces fall back to their first
        edge as u. Artwork coordinates use millimeters in this chart. Indices
        refer to the supplied face order, regardless of painter sorting.
        """
        if not 0 <= index < len(self.faces):
            raise IndexError("Face index is outside the face array.")
        points = tuple(self.vertices[i] for i in self.faces[index])
        normal = face_normal(points)
        up = Vector3D(0, 0, 1)
        tangent = up + normal * -up.dot(normal)
        if tangent.length > 1e-10:
            v = tangent.normalized()
            u = v.cross(normal)
        else:
            u = (points[1] - points[0]).normalized()
            v = normal.cross(u)
        return Plane3D(centroid(points), u, v)

    def with_face_artwork(
        self,
        index: int,
        graphic: Graphic,
        style: Style | None = None,
        *,
        transform: Transform = Transform(),
    ) -> Polyhedron:
        """Return a solid with 2D artwork attached to one face's local chart.

        Artwork replaces the previous entry for this face. It is not clipped
        or lit automatically, so keep it within the face boundary. Text follows
        the plane transform (outlined under perspective).
        Back-facing artwork is retained and mirrored; opaque and transparent
        faces use the same approximate center-depth sort.
        Mutable built-ins are captured when Scene3D.project is called.
        """
        self.face_plane(index)
        artwork = list(self.face_artwork or (None,) * len(self.faces))
        artwork[index] = Drawing(graphic, style, transform)
        return replace(self, face_artwork=tuple(artwork))

    def transformed(self, transform: Transform3D) -> Polyhedron:
        """Transform geometry, transporting existing artwork charts with it.

        Outward winding is preserved under reflection. Artwork's new local
        matrix retains its original physical placement, including nonuniform
        scaling, instead of resetting to the new face's unit chart.
        """
        determinant = transform.x.dot(transform.y.cross(transform.z))
        faces = tuple(tuple(reversed(f)) for f in self.faces) if determinant < 0 else self.faces
        result = replace(
            self,
            vertices=tuple(transform.apply(p) for p in self.vertices),
            faces=faces,
            face_artwork=None,
        )
        if self.face_artwork is None:
            return result
        artwork: list[Drawing | None] = []
        for i, drawing in enumerate(self.face_artwork):
            if drawing is None:
                artwork.append(None)
                continue
            old = self.face_plane(i).transformed(transform)
            new = result.face_plane(i)
            offset = old.origin - new.origin
            matrix = Transform(
                old.u.dot(new.u),
                old.u.dot(new.v),
                old.v.dot(new.u),
                old.v.dot(new.v),
                offset.dot(new.u),
                offset.dot(new.v),
            )
            artwork.append(drawing.transformed(matrix))
        return replace(result, face_artwork=tuple(artwork))


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
