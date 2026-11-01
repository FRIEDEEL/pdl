"""Smooth sphere/cylinder descriptions and portable vector gradient projection."""

from __future__ import annotations

from dataclasses import dataclass
from math import cos, hypot, isfinite, pi, sqrt
from typing import TYPE_CHECKING

from pdl.author.entity.base import Entity
from pdl.author.geometry.path import Path
from pdl.author.geometry.shapes import Arc, Circle
from pdl.author.style import BLACK, Color, ColorStop, LinearGradient, RadialGradient, Style
from pdl.author.transform.affine import AffineTransform as Transform
from pdl.author.transform.affine import Scaling, Translation
from pdl.extensions.spacial._author import make_entity, make_group
from pdl.extensions.spacial.coordinates import Point3D, Vector3D

if TYPE_CHECKING:
    from pdl.extensions.spacial.projection import DirectionalLight, OrthographicCamera


@dataclass(frozen=True)
class Sphere:
    """A sphere with a smooth, approximate radial-gradient fill.

    Args:
        center: World center in millimeters.
        radius: Positive radius in millimeters.
        color: Intrinsic RGB color.
        stroke: Silhouette color, or None to omit it.
        line_width: Silhouette width in Canvas millimeters.

    Orthographic projection preserves the circular silhouette. Lighting shifts
    a concentric radial gradient toward the projected light source; this is a
    diagram approximation, not pointwise Lambert shading. No facets or raster
    images are generated. A sphere sorts as one item at its center depth.
    """

    center: Point3D = Point3D(0, 0, 0)
    radius: float = 10
    color: Color = Color(0.35, 0.65, 0.9)
    stroke: Color | None = BLACK
    line_width: float = 0.25

    def __post_init__(self) -> None:
        _validate_size(self.radius)
        Style(stroke=self.stroke, line_width=self.line_width)


@dataclass(frozen=True)
class Cylinder:
    """A closed circular cylinder with a smooth axial-invariant side gradient.

    Args:
        base: World center of the base disk in millimeters.
        radius: Positive radius in millimeters.
        height: Positive distance from base to top in millimeters.
        axis: Nonzero direction from base toward top; magnitude is ignored.
        color: Intrinsic RGB color, shared by side and caps.
        stroke: Visible outline/rim color, or None.
        line_width: Outline width in Canvas millimeters.

    The visible side uses 33 Lambert-sampled linear-gradient stops; caps have
    constant normals and solid colors. Elliptical boundaries use cubic Bezier
    arc approximations, not surface facets. Only the facing cap is drawn.
    The cylinder sorts as one item at its axial midpoint; intersections and
    interleaving with other solids are not resolved.
    """

    base: Point3D = Point3D(0, 0, 0)
    radius: float = 10
    height: float = 25
    axis: Vector3D = Vector3D(0, 0, 1)
    color: Color = Color(0.35, 0.65, 0.9)
    stroke: Color | None = BLACK
    line_width: float = 0.25

    def __post_init__(self) -> None:
        _validate_size(self.radius)
        _validate_size(self.height)
        self.axis.normalized()
        Style(stroke=self.stroke, line_width=self.line_width)

    @property
    def center(self) -> Point3D:
        """World midpoint used for scene depth sorting."""
        return self.base + self.axis.normalized() * (self.height / 2)


def _validate_size(value: float) -> None:
    if not isfinite(value) or value <= 0:
        raise ValueError("Dimensions must be finite and positive.")


def project_sphere(
    sphere: Sphere, camera: OrthographicCamera, light: DirectionalLight | None
) -> Entity:
    """Lower a sphere to one circle and a portable radial gradient."""
    fill: Color | RadialGradient = sphere.color
    if light is not None:
        source = light.direction.normalized() * -1
        x, y, z = (source.dot(v) for v in (camera.right, camera.up, camera.toward_viewer))
        lateral = min(1.0, hypot(x, y))
        peak = 1.0 if z >= 0 else lateral
        stops: list[ColorStop] = []
        for i in range(33):
            t = i / 32
            intensity = light.ambient + (1 - light.ambient) * peak * (1 + cos(pi * t)) / 2
            stops.append(
                ColorStop(
                    t,
                    Color(
                        sphere.color.red * intensity,
                        sphere.color.green * intensity,
                        sphere.color.blue * intensity,
                    ),
                )
            )
        fill = RadialGradient(
            tuple(stops), center=(0.5 + 0.35 * x, 0.5 + 0.35 * y), radius=0.5 + 0.15 * lateral
        )
    return make_entity(
        Circle(camera.project(sphere.center), sphere.radius),
        Style(fill=fill, stroke=sphere.stroke, line_width=sphere.line_width),
    )


def project_cylinder(
    cylinder: Cylinder, camera: OrthographicCamera, light: DirectionalLight | None
) -> Entity:
    """Lower a cylinder to one curved side patch and one facing disk."""
    axis = cylinder.axis.normalized()
    viewer = camera.toward_viewer
    cosine = max(-1.0, min(1.0, axis.dot(viewer)))
    front_vector = viewer + axis * -cosine
    sine = front_vector.length
    cap_normal = axis if cosine >= 0 else axis * -1
    cap_color = cylinder.color if light is None else light.shade(cylinder.color, cap_normal)
    cap_style = Style(fill=cap_color, stroke=cylinder.stroke, line_width=cylinder.line_width)
    if sine < 1e-8:
        cap_center = cylinder.base + axis * cylinder.height if cosine >= 0 else cylinder.base
        return make_entity(Circle(camera.project(cap_center), cylinder.radius), cap_style)

    front = front_vector.normalized()
    side = axis.cross(front).normalized()
    along_x, along_y = axis.dot(camera.right) / sine, axis.dot(camera.up) / sine
    origin = camera.project(cylinder.base)
    placement = Transform(
        side.dot(camera.right), side.dot(camera.up), along_x, along_y, origin.x, origin.y
    )
    radius, height = cylinder.radius, cylinder.height * sine
    ellipse_y = radius * abs(cosine)
    sweep = 180 if cosine >= 0 else -180
    path = Path().move_to((-radius, 0))
    if ellipse_y > 1e-10:
        path.arc(Arc((0, 0), radius, ellipse_y, 180, sweep))
    else:
        path.line_to((radius, 0))
    path.line_to((radius, height))
    if ellipse_y > 1e-10:
        path.arc(Arc((0, height), radius, ellipse_y, 0, -sweep))
    else:
        path.line_to((-radius, height))
    path.close()
    fill: Color | LinearGradient = cylinder.color
    if light is not None:
        stops: list[ColorStop] = []
        for i in range(33):
            t = i / 32
            q = 2 * t - 1
            normal = side * q + front * sqrt(max(0, 1 - q * q))
            stops.append(ColorStop(t, light.shade(cylinder.color, normal)))
        fill = LinearGradient(tuple(stops), start=(0, 0), end=(1, 0))
    drawings = [
        make_entity(
            path,
            Style(
                fill=fill, stroke=cylinder.stroke, line_width=cylinder.line_width, line_join="round"
            ),
        )
    ]
    if ellipse_y > 1e-10:
        cap_y = height if cosine >= 0 else 0
        # Circle + affine placement retains native circle/ellipse opportunities.
        cap = make_entity(
            Circle((0, 0), 1),
            cap_style,
            Translation(0, cap_y) @ Scaling(radius, ellipse_y),
        )
        drawings.append(cap)
    return make_entity(make_group(tuple(drawings)), transform=placement)
