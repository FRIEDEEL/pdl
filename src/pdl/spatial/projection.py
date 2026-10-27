"""Orthographic cameras, directional flat shading and painter ordering."""

from dataclasses import dataclass
from math import cos, isfinite, radians, sin

from pdl.geometry.primitives import Point, Polygon
from pdl.geometry.transforms import Transform
from pdl.scene.composition import Drawing
from pdl.scene.paint import Color, Style
from pdl.spatial.coordinates import Point3D, Vector3D
from pdl.spatial.solids import Polyhedron, Surface3D, centroid, face_normal


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
    object/face order for manual control. Separate scenes follow Canvas order.
    """

    objects: tuple[Polyhedron | Surface3D, ...]
    camera: OrthographicCamera = OrthographicCamera()
    light: DirectionalLight | None = DirectionalLight()
    sort_faces: bool = True

    def decompose(self) -> tuple[Drawing, ...]:
        """Return projected vector drawings with per-face solid colors."""
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
                    items.append((self.camera.depth(centroid(points)), drawing))
            else:
                origin = self.camera.project(obj.plane.origin)
                u = obj.plane.u
                v = obj.plane.v
                matrix = Transform(
                    u.dot(self.camera.right),
                    u.dot(self.camera.up),
                    v.dot(self.camera.right),
                    v.dot(self.camera.up),
                    origin.x,
                    origin.y,
                )
                items.append((self.camera.depth(obj.depth_point), obj.drawing.transformed(matrix)))
        if self.sort_faces:
            items.sort(key=lambda item: item[0])
        return tuple(drawing for _, drawing in items)
