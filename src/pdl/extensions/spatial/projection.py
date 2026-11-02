"""Cameras, directional shading and BSP or approximate polygon ordering."""

from copy import deepcopy as capture
from dataclasses import dataclass
from math import cos, isfinite, radians, sin
from typing import Literal
from warnings import warn

from pdl.author.entity.base import Entity
from pdl.author.geometry.point import Point
from pdl.author.geometry.shapes import Line, Polygon
from pdl.author.style import Color, Style
from pdl.author.transform.affine import AffineTransform
from pdl.extensions.spatial._author import make_entity, make_group
from pdl.extensions.spatial.coordinates import Point3D, Vector3D
from pdl.extensions.spatial.curves import Cylinder, Sphere, project_cylinder, project_sphere
from pdl.extensions.spatial.planar import PerspectiveArtwork
from pdl.extensions.spatial.projected import ProjectedScene
from pdl.extensions.spatial.solids import Plane3D, Polyhedron, Surface3D, centroid, face_normal
from pdl.extensions.spatial.surfaces import (
    AnnularCylinder,
    CylinderSurface,
    project_annular_cylinder,
    project_cylinder_surface,
)
from pdl.extensions.spatial.visibility import (
    Fragment,
    Metrics,
    build,
    convex_fragments,
    ordered,
)


@dataclass(frozen=True)
class DirectionalLight:
    """Parallel light traveling along direction in world coordinates.

    RGB channels are multiplied directly by
    ``ambient + (1-ambient) * max(0, -normal.dot(direction))``.
    Both vectors are normalized. This is a simple diagram color mapping,
    without gamma conversion, shadows, attenuation or specular reflection.
    """

    direction: Vector3D = Vector3D(-1, -2, -3)
    ambient: float = 0.25

    def __post_init__(self) -> None:
        self.direction.normalized()
        if not isfinite(self.ambient) or not 0 <= self.ambient <= 1:
            raise ValueError("Ambient light must be between zero and one.")

    def shade(self, color: Color, normal: Vector3D) -> Color:
        """Map intrinsic color and world face normal to a flat face color."""
        cosine = max(0.0, min(1.0, -normal.normalized().dot(self.direction.normalized())))
        intensity = self.ambient + (1 - self.ambient) * cosine
        return Color(color.red * intensity, color.green * intensity, color.blue * intensity)


@dataclass(frozen=True)
class OrthographicCamera:
    """View the target from azimuth/elevation angles, in degrees.

    World +z is up. Azimuth is measured from +x toward +y; elevation is
    measured above the xy plane. Default angles give an isometric view.
    Projection retains millimeters; target projects to (0, 0). Larger depth
    is closer to the viewer. There is no perspective or near/far clipping.
    """

    azimuth: float = 45
    elevation: float = 35.264389682754654
    target: Point3D = Point3D(0, 0, 0)

    def __post_init__(self) -> None:
        if not all(isfinite(a) for a in (self.azimuth, self.elevation)):
            raise ValueError("Camera angles must be finite.")

    @property
    def right(self) -> Vector3D:
        a = radians(self.azimuth)
        return Vector3D(-sin(a), cos(a), 0)

    @property
    def up(self) -> Vector3D:
        a, e = radians(self.azimuth), radians(self.elevation)
        return Vector3D(-sin(e) * cos(a), -sin(e) * sin(a), cos(e))

    @property
    def toward_viewer(self) -> Vector3D:
        return self.right.cross(self.up)

    def project(self, point: Point3D) -> Point:
        """Project a world point into 2D millimeter coordinates."""
        offset = point - self.target
        return Point(offset.dot(self.right), offset.dot(self.up))

    def depth(self, point: Point3D) -> float:
        return (point - self.target).dot(self.toward_viewer)


@dataclass(frozen=True)
class PerspectiveCamera(OrthographicCamera):
    """Pinhole camera looking at target with the same angle convention as orthographic.

    Args:
        distance: Eye-to-target distance in millimeters, default 100.
        focal_length: Eye-to-image-plane distance in millimeters, default 100.
        near: Minimum permitted eye-space distance in millimeters, default 0.1.

    The eye is target + distance*toward_viewer. The target maps to (0, 0);
    its plane has scale focal_length/distance. Larger depth is closer, as for
    OrthographicCamera; it is axial depth, not Euclidean distance to the eye.
    Points at or behind near raise ValueError; geometry is never clipped.
    Only polygon solids and path-compatible planar artwork are supported.
    """

    distance: float = 100
    focal_length: float = 100
    near: float = 0.1

    def __post_init__(self) -> None:
        super().__post_init__()
        if not all(isfinite(v) and v > 0 for v in (self.distance, self.focal_length, self.near)):
            raise ValueError("Perspective distances must be finite and positive.")
        if self.near >= self.distance:
            raise ValueError("Near distance must be smaller than eye-to-target distance.")

    @property
    def eye(self) -> Point3D:
        """World position of the pinhole."""
        return self.target + self.toward_viewer * self.distance

    def project(self, point: Point3D) -> Point:
        """Project a point; reject points at or behind the near plane."""
        axial = self.distance - self.depth(point)
        if axial <= self.near:
            raise ValueError(
                "Perspective geometry must lie beyond the near plane; clipping is unsupported."
            )
        flat = super().project(point)
        scale = self.focal_length / axial
        return Point(flat.x * scale, flat.y * scale)


@dataclass(frozen=True)
class Scene3D:
    """Project solids and planar drawings into an ordinary 2D composite.

    ``visibility="auto"`` uses BSP for scenes containing only Polyhedron objects
    without face artwork. Simple concave loops are triangulated as needed;
    intersecting faces and visibility cycles are split into ordered fragments.
    Opacity is composited back-to-front, without refraction or solid booleans.
    Coplanar ties follow input object/face order. No backface culling is used.

    Curved solids, free planar drawings and face artwork require approximate
    centroid ordering: auto emits a warning and records this mode in the result;
    choose ``visibility="centroid"`` to acknowledge it explicitly, or "bsp" to
    reject unsupported scenes. This selection applies to the entire scene.
    ``sort_faces=False`` bypasses all sorting and splitting, preserving input
    object/face order, independently of visibility. Separate scenes follow
    ordinary 2D Canvas order.

    Args:
        objects: Captured solids and surface drawings, in source-index order.
        camera: Orthographic or perspective camera. Curved solids are orthographic only.
        light: Optional directional shading, evaluated before splitting.
        sort_faces: False selects manual source order without triangulation.
        visibility: Auto BSP selection, mandatory BSP, or approximate centroid sorting.
        bsp_tolerance: Positive finite absolute world-plane tolerance in mm (1e-8).
        max_fragments: Positive fragment budget including triangulation (100000).

    BSP uses floating predicates, not exact arithmetic. A 500-level tree safety
    limit and the fragment budget raise ValueError; no fallback is attempted.
    New cut edges receive no stroke. Near-plane crossings still raise errors.
    Face artwork clipping and inter-object curved-surface visibility are not provided.
    """

    objects: tuple[
        Polyhedron | Surface3D | Sphere | Cylinder | CylinderSurface | AnnularCylinder, ...
    ]
    camera: OrthographicCamera | PerspectiveCamera = OrthographicCamera()
    light: DirectionalLight | None = DirectionalLight()
    sort_faces: bool = True
    visibility: Literal["auto", "bsp", "centroid"] = "auto"
    bsp_tolerance: float = 1e-8
    max_fragments: int = 100_000

    def __post_init__(self) -> None:
        if self.visibility not in ("auto", "bsp", "centroid"):
            raise ValueError("visibility must be auto, bsp or centroid.")
        if not isfinite(self.bsp_tolerance) or self.bsp_tolerance <= 0:
            raise ValueError("bsp_tolerance must be finite and positive.")
        if type(self.max_fragments) is not int or self.max_fragments < 1:
            raise ValueError("max_fragments must be a positive integer.")

    def _visibility_mode(self) -> Literal["bsp", "centroid", "manual"]:
        if not self.sort_faces:
            return "manual"
        supported = all(
            isinstance(obj, Polyhedron)
            and (obj.face_artwork is None or all(a is None for a in obj.face_artwork))
            for obj in self.objects
        )
        if self.visibility == "bsp" and not supported:
            raise ValueError(
                "BSP requires polyhedra without face artwork; use visibility='centroid' "
                "for curved solids or planar artwork (approximate ordering)."
            )
        if self.visibility == "auto" and not supported:
            warn(
                "Scene3D uses approximate centroid ordering for curved solids or planar artwork; "
                "set visibility='centroid' explicitly to acknowledge this boundary.",
                UserWarning,
                stacklevel=3,
            )
        return "bsp" if supported and self.visibility != "centroid" else "centroid"

    def _bsp_drawings(self) -> tuple[tuple[Entity, ...], tuple[tuple[int, int], ...]]:

        fragments: list[Fragment] = []
        sources: list[tuple[int, int]] = []
        paints: list[Style] = []
        for object_index, obj in enumerate(self.objects):
            if not isinstance(obj, Polyhedron):
                raise TypeError("BSP requires polygon solids.")
            # Fail before tree construction when any source vertex crosses near.
            for vertex in obj.vertices:
                self.camera.project(vertex)
            for face_index, face in enumerate(obj.faces):
                points = tuple(obj.vertices[index] for index in face)
                color = obj.color if obj.face_colors is None else obj.face_colors[face_index]
                if self.light is not None:
                    color = self.light.shade(color, face_normal(points))
                fragments.extend(convex_fragments(points, len(sources), self.bsp_tolerance))
                sources.append((object_index, face_index))
                paints.append(
                    Style(
                        fill=color,
                        stroke=obj.stroke,
                        line_width=obj.line_width,
                        line_join="round",
                        opacity=obj.opacity,
                    )
                )
                if len(fragments) > self.max_fragments:
                    raise ValueError(f"BSP fragment budget exceeded ({self.max_fragments}).")
        metrics = Metrics(input_faces=len(fragments))
        tree = build(tuple(fragments), metrics, self.bsp_tolerance, self.max_fragments)
        viewer = (
            self.camera.eye
            if isinstance(self.camera, PerspectiveCamera)
            else self.camera.toward_viewer
        )
        result: list[Entity] = []
        correspondence: list[tuple[int, int]] = []
        for fragment in ordered(tree, viewer):
            points = tuple(self.camera.project(p) for p in fragment.vertices)
            paint = paints[fragment.source]
            if all(fragment.boundary):
                drawing = make_entity(Polygon(points), paint)
            else:
                # Paint fragments atomically. Never stroke new BSP/triangulation cuts.
                fill = make_entity(
                    Polygon(points), Style(stroke=None, fill=paint.fill, opacity=paint.opacity)
                )
                edges = tuple(
                    make_entity(
                        Line(a, points[(i + 1) % len(points)]),
                        Style(
                            stroke=paint.stroke, line_width=paint.line_width, opacity=paint.opacity
                        ),
                    )
                    for i, a in enumerate(points)
                    if fragment.boundary[i] and paint.stroke is not None and paint.line_width > 0
                )
                drawing = make_entity(make_group((fill, *edges)))
            result.append(drawing)
            correspondence.append(sources[fragment.source])
        return tuple(result), tuple(correspondence)

    def project(self) -> ProjectedScene:
        """Capture a 2D authoring snapshot without measuring text or rendering.

        Projection fixes camera, geometry, lighting and painter order for this
        snapshot. BSP sorting and face splitting are confined to this call's
        objects. Independently projected scenes never participate in each other's
        visibility calculations: Canvas paint order controls their overlap.
        Share a camera and world frame to align separate projections; apply the
        same 2D placement to keep them aligned. Add 2D legends and references
        afterward, then let Canvas resolve the complete 2D description. Re-project
        to change geometry or view; 2D edits never modify the source scene.
        """
        source = capture(self)
        return source._project()

    def decompose(self) -> tuple[Entity, ...]:
        """Compatibility shorthand; prefer explicitly drawing self.project()."""
        return self.project().decompose()

    def _project(self) -> ProjectedScene:
        mode = self._visibility_mode()
        if mode == "bsp":
            children, source_faces = self._bsp_drawings()
        else:
            children, source_faces = self._centroid_drawings()
        vertices = tuple(
            tuple(self.camera.project(p) for p in obj.vertices)
            if isinstance(obj, Polyhedron)
            else ()
            for obj in self.objects
        )
        centers = tuple(
            tuple(
                self.camera.project(centroid(tuple(obj.vertices[i] for i in face)))
                for face in obj.faces
            )
            if isinstance(obj, Polyhedron)
            else ()
            for obj in self.objects
        )
        right, up = self.camera.right, self.camera.up
        return ProjectedScene(
            children,
            vertices,
            centers,
            self.camera.target,
            (right.x, right.y, right.z),
            (up.x, up.y, up.z),
            self.camera.distance if isinstance(self.camera, PerspectiveCamera) else None,
            self.camera.focal_length if isinstance(self.camera, PerspectiveCamera) else 100,
            self.camera.near if isinstance(self.camera, PerspectiveCamera) else 0.1,
            visibility=mode,
            source_faces=source_faces,
        )

    def _centroid_drawings(self) -> tuple[tuple[Entity, ...], tuple[tuple[int, int] | None, ...]]:
        items: list[tuple[float, Entity, tuple[int, int] | None]] = []
        for object_index, obj in enumerate(self.objects):
            if isinstance(obj, Polyhedron):
                for i, face in enumerate(obj.faces):
                    points = tuple(obj.vertices[index] for index in face)
                    color = obj.color if obj.face_colors is None else obj.face_colors[i]
                    if self.light is not None:
                        color = self.light.shade(color, face_normal(points))
                    drawing = make_entity(
                        Polygon(tuple(self.camera.project(p) for p in points)),
                        Style(
                            fill=color,
                            stroke=obj.stroke,
                            line_width=obj.line_width,
                            line_join="round",
                            opacity=obj.opacity,
                        ),
                    )
                    artwork = None if obj.face_artwork is None else obj.face_artwork[i]
                    if artwork is not None:
                        surface = obj.face_plane(i)
                        overlay = self._plane_drawing(surface, artwork)
                        drawing = make_entity(make_group((drawing, overlay)))
                    items.append((self.camera.depth(centroid(points)), drawing, (object_index, i)))
            elif isinstance(obj, (Sphere, Cylinder, CylinderSurface, AnnularCylinder)):
                if isinstance(self.camera, PerspectiveCamera):
                    raise ValueError("Curved objects currently require OrthographicCamera.")
                if isinstance(obj, Sphere):
                    drawing = project_sphere(obj, self.camera, self.light)
                elif isinstance(obj, Cylinder):
                    drawing = project_cylinder(obj, self.camera, self.light)
                elif isinstance(obj, CylinderSurface):
                    drawing = project_cylinder_surface(obj, self.camera)
                else:
                    drawing = project_annular_cylinder(obj, self.camera)
                items.append((self.camera.depth(obj.center), drawing, None))
            else:
                items.append(
                    (
                        self.camera.depth(obj.depth_point),
                        self._plane_drawing(obj.plane, obj.drawing),
                        None,
                    )
                )
        if self.sort_faces:
            items.sort(key=lambda item: item[0])
        return tuple(item[1] for item in items), tuple(item[2] for item in items)

    def _plane_drawing(self, plane: Plane3D, drawing: Entity) -> Entity:
        if isinstance(self.camera, PerspectiveCamera):
            return make_entity(PerspectiveArtwork(plane, drawing, self.camera))
        return drawing.copy().apply_transform(self._plane_matrix(plane))

    def _plane_matrix(self, plane: Plane3D) -> AffineTransform:
        origin = self.camera.project(plane.origin)
        return AffineTransform(
            plane.u.dot(self.camera.right),
            plane.u.dot(self.camera.up),
            plane.v.dot(self.camera.right),
            plane.v.dot(self.camera.up),
            origin.x,
            origin.y,
        )
