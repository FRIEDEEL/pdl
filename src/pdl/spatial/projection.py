"""Orthographic cameras, directional flat shading and painter ordering."""

from dataclasses import dataclass
from math import cos, isfinite, radians, sin

from pdl.geometry.primitives import Point, Polygon
from pdl.geometry.transforms import Transform
from pdl.scene.authoring import capture
from pdl.scene.composition import Drawing, GroupDescription
from pdl.scene.paint import Color, Style
from pdl.spatial.coordinates import Point3D, Vector3D
from pdl.spatial.curves import Cylinder, Sphere, project_cylinder, project_sphere
from pdl.spatial.projected import ProjectedScene
from pdl.spatial.solids import Plane3D, Polyhedron, Surface3D, centroid, face_normal


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
class Scene3D:
    """Project solids and planar drawings into an ordinary 2D composite.

    All faces in one scene are sorted together, far to near, by centroid
    depth. Surface placements use their explicit depth reference. No face
    splitting, intersection resolution, hidden-line extraction or backface
    culling is performed. Painter ordering can fail for overlapping depth
    intervals or cyclic occlusion. ``sort_faces=False`` preserves supplied
    object/face order for manual control. Spheres and cylinders sort as whole
    objects by center depth. Separate scenes follow Canvas order.
    """

    objects: tuple[Polyhedron | Surface3D | Sphere | Cylinder, ...]
    camera: OrthographicCamera = OrthographicCamera()
    light: DirectionalLight | None = DirectionalLight()
    sort_faces: bool = True

    def project(self) -> ProjectedScene:
        """Capture a 2D authoring snapshot without measuring text or rendering.

        Projection fixes camera, geometry, lighting and painter order for this
        snapshot. Add 2D legends and references afterward, then let Canvas
        resolve the complete 2D description. Re-project to change the view.
        """
        source = capture(self)
        return source._project()

    def decompose(self) -> tuple[Drawing, ...]:
        """Compatibility shorthand; prefer explicitly drawing self.project()."""
        return self.project().decompose()

    def _project(self) -> ProjectedScene:
        items: list[tuple[float, Drawing]] = []
        for obj in self.objects:
            if isinstance(obj, Polyhedron):
                for i, face in enumerate(obj.faces):
                    points = tuple(obj.vertices[index] for index in face)
                    color = obj.color if obj.face_colors is None else obj.face_colors[i]
                    if self.light is not None:
                        color = self.light.shade(color, face_normal(points))
                    drawing = Drawing(
                        Polygon(tuple(self.camera.project(p) for p in points)),
                        Style(
                            fill=color,
                            stroke=obj.stroke,
                            line_width=obj.line_width,
                            line_join="round",
                        ),
                    )
                    artwork = None if obj.face_artwork is None else obj.face_artwork[i]
                    normal = face_normal(points)
                    if artwork is not None and normal.dot(self.camera.toward_viewer) > 1e-10:
                        surface = obj.face_plane(i)
                        overlay = artwork.transformed(self._plane_matrix(surface))
                        drawing = Drawing(GroupDescription((drawing, overlay)))
                    items.append((self.camera.depth(centroid(points)), drawing))
            elif isinstance(obj, (Sphere, Cylinder)):
                drawing = (
                    project_sphere(obj, self.camera, self.light)
                    if isinstance(obj, Sphere)
                    else project_cylinder(obj, self.camera, self.light)
                )
                items.append((self.camera.depth(obj.center), drawing))
            else:
                items.append(
                    (
                        self.camera.depth(obj.depth_point),
                        obj.drawing.transformed(self._plane_matrix(obj.plane)),
                    )
                )
        if self.sort_faces:
            items.sort(key=lambda item: item[0])
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
            tuple(drawing for _, drawing in items),
            vertices,
            centers,
            self.camera.target,
            (right.x, right.y, right.z),
            (up.x, up.y, up.z),
        )

    def _plane_matrix(self, plane: Plane3D) -> Transform:
        origin = self.camera.project(plane.origin)
        return Transform(
            plane.u.dot(self.camera.right),
            plane.u.dot(self.camera.up),
            plane.v.dot(self.camera.right),
            plane.v.dot(self.camera.up),
            origin.x,
            origin.y,
        )
