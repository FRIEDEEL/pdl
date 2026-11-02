"""Smooth cylindrical surfaces for explicitly layered scientific illustrations."""

from __future__ import annotations

from dataclasses import dataclass, replace
from math import atan2, ceil, cos, isclose, isfinite, pi, radians, sin, tan
from typing import TYPE_CHECKING, Self

from pdl.author.entity.base import Entity
from pdl.author.geometry.path import Path
from pdl.author.style import BLACK, Color, Style
from pdl.extensions.spatial._author import make_entity, make_group
from pdl.extensions.spatial.coordinates import Point3D, Transform3D, Vector3D

if TYPE_CHECKING:
    from pdl.extensions.spatial.projection import OrthographicCamera


@dataclass(frozen=True)
class CylinderSurface:
    """An open, two-sided circular cylinder side, without thickness or end caps.

    Args:
        base: Base-circle center in world millimeters.
        radius: Positive radius in millimeters.
        height: Positive axial length in millimeters.
        axis: Nonzero axial direction; its magnitude is ignored.
        radial: Nonzero direction perpendicular to axis, defining angle zero.
            Its magnitude is ignored. Positive angles follow axis cross radial.
        start_angle: Finite start angle in degrees, default 0.
        sweep_angle: Positive angular extent up to 360 degrees, default 180.
        color: Uniform fill on both sides; scene lighting is not applied.
        stroke: Boundary and silhouette color, or None.
        line_width: Stroke width in Canvas millimeters, default 0.25.

    A half-cylinder is the default. Curves use cubic Bezier arc approximations
    of at most 45 degrees; no polygon mesh is generated. Orthographic cameras
    only. Visible branches are painted back-to-front within this object, but
    intersections with other objects are not resolved. Use separate projections
    and Canvas order for intentional illustration layers. BSP rejects this type.
    Instances are immutable; use dataclasses.replace or transformed for edits.
    """

    base: Point3D = Point3D(0, 0, 0)
    radius: float = 10
    height: float = 25
    axis: Vector3D = Vector3D(0, 0, 1)
    radial: Vector3D = Vector3D(1, 0, 0)
    start_angle: float = 0
    sweep_angle: float = 180
    color: Color = Color(0.35, 0.65, 0.9)
    stroke: Color | None = BLACK
    line_width: float = 0.25

    def __post_init__(self) -> None:
        _dimensions(self.radius, self.height)
        _basis(self.axis, self.radial)
        if not isfinite(self.start_angle):
            raise ValueError("start_angle must be finite.")
        if not isfinite(self.sweep_angle) or not 0 < self.sweep_angle <= 360:
            raise ValueError("sweep_angle must be positive and at most 360 degrees.")
        Style(stroke=self.stroke, line_width=self.line_width)

    @property
    def center(self) -> Point3D:
        """Axial midpoint used only for approximate inter-object depth sorting."""
        return self.base + self.axis.normalized() * (self.height / 2)

    def point(self, angle: float, height: float = 0) -> Point3D:
        """Return a world point at an angle in degrees and an axial height in mm.

        Coordinates may lie outside the authored angular/height range; this is
        a coordinate query, not a clipping or visibility test.
        """
        axis, u, v = _basis(self.axis, self.radial)
        a = radians(angle)
        return self.base + axis * height + u * (self.radius * cos(a)) + v * (self.radius * sin(a))

    def transformed(self, transform: Transform3D) -> Self:
        """Return a translated, rotated, reflected or uniformly scaled copy.

        Nonuniform scale, shear and singular transforms raise ValueError because
        they do not preserve this circular-cylinder representation.
        """
        scale = _similarity_scale(transform)
        return replace(
            self,
            base=transform.apply(self.base),
            axis=transform.apply_vector(self.axis),
            radial=transform.apply_vector(self.radial),
            radius=self.radius * scale,
            height=self.height * scale,
            # A reflection reverses the right-handed angular convention.
            start_angle=(
                -self.start_angle - self.sweep_angle if _reflected(transform) else self.start_angle
            ),
        )


@dataclass(frozen=True)
class AnnularCylinder:
    """A closed washer with cylindrical inner/outer walls and annular end caps.

    Args:
        base: Base-circle center in world millimeters.
        outer_radius: Positive outer radius in millimeters, default 10.
        inner_radius: Positive bore radius smaller than outer_radius, default 5.
        height: Positive axial thickness in millimeters, default 5.
        axis: Nonzero base-to-top direction; magnitude is ignored.
        color: Uniform fill; scene lighting is not applied.
        stroke: Visible rim/silhouette color, or None.
        line_width: Width in Canvas millimeters, default 0.25.

    Orthographic projection keeps the central opening empty and paints the
    visible inner wall, outer wall and facing cap in order. Boundaries are
    smooth Bezier approximations without facets. No inter-object intersection,
    boolean cutting or automatic probe clipping is performed. BSP rejects this
    type; independently projected layers follow Canvas paint order.
    """

    base: Point3D = Point3D(0, 0, 0)
    outer_radius: float = 10
    inner_radius: float = 5
    height: float = 5
    axis: Vector3D = Vector3D(0, 0, 1)
    color: Color = Color(0.35, 0.65, 0.9)
    stroke: Color | None = BLACK
    line_width: float = 0.25

    def __post_init__(self) -> None:
        _dimensions(self.outer_radius, self.inner_radius, self.height)
        self.axis.normalized()
        if self.inner_radius >= self.outer_radius:
            raise ValueError("inner_radius must be smaller than outer_radius.")
        Style(stroke=self.stroke, line_width=self.line_width)

    @property
    def center(self) -> Point3D:
        """Axial midpoint used for approximate inter-object depth sorting."""
        return self.base + self.axis.normalized() * (self.height / 2)

    def transformed(self, transform: Transform3D) -> Self:
        """Return a similarity-transformed copy; reject shear/nonuniform scale."""
        scale = _similarity_scale(transform)
        return replace(
            self,
            base=transform.apply(self.base),
            axis=transform.apply_vector(self.axis),
            outer_radius=self.outer_radius * scale,
            inner_radius=self.inner_radius * scale,
            height=self.height * scale,
        )


def _dimensions(*values: float) -> None:
    if any(not isfinite(x) or x <= 0 for x in values):
        raise ValueError("Dimensions must be finite and positive.")


def _basis(axis: Vector3D, radial: Vector3D) -> tuple[Vector3D, Vector3D, Vector3D]:
    w, u = axis.normalized(), radial.normalized()
    if abs(w.dot(u)) > 1e-10:
        raise ValueError("radial must be perpendicular to axis.")
    return w, u, w.cross(u).normalized()


def _reflected(transform: Transform3D) -> bool:
    return transform.x.dot(transform.y.cross(transform.z)) < 0


def _similarity_scale(transform: Transform3D) -> float:
    vectors = (transform.x, transform.y, transform.z)
    scale = vectors[0].length
    if scale == 0 or any(not isclose(v.length, scale, rel_tol=1e-10) for v in vectors):
        raise ValueError("Circular surfaces require a nonsingular uniform scale.")
    if any(
        abs(a.normalized().dot(b.normalized())) > 1e-10
        for a, b in ((vectors[0], vectors[1]), (vectors[0], vectors[2]), (vectors[1], vectors[2]))
    ):
        raise ValueError("Circular surfaces do not support shear.")
    return scale


def _arc(
    path: Path,
    surface: CylinderSurface,
    camera: OrthographicCamera,
    start: float,
    end: float,
    height: float,
) -> None:
    """Append an affine-projected circular arc, without connecting a subpath."""
    _, u, v = _basis(surface.axis, surface.radial)
    count = max(1, ceil(abs(end - start) / (pi / 4)))
    for i in range(count):
        a = start + (end - start) * i / count
        b = start + (end - start) * (i + 1) / count
        k = 4 / 3 * tan((b - a) / 4) * surface.radius
        p, q = surface.point(a * 180 / pi, height), surface.point(b * 180 / pi, height)
        tangent_a = u * -sin(a) + v * cos(a)
        tangent_b = u * -sin(b) + v * cos(b)
        path.cubic_to(
            camera.project(p + tangent_a * k), camera.project(q + tangent_b * -k), camera.project(q)
        )


def _patch(
    surface: CylinderSurface,
    camera: OrthographicCamera,
    start: float,
    end: float,
) -> Entity:
    bottom_start = camera.project(surface.point(start * 180 / pi))
    path = Path().move_to(bottom_start)
    _arc(path, surface, camera, start, end, 0)
    path.line_to(camera.project(surface.point(end * 180 / pi, surface.height)))
    _arc(path, surface, camera, end, start, surface.height)
    path.close()
    fill = make_entity(path, Style(fill=surface.color, stroke=None))
    outline = Path().move_to(bottom_start)
    _arc(outline, surface, camera, start, end, 0)
    _, u, v = _basis(surface.axis, surface.radial)

    def vertical_boundary(angle: float) -> bool:
        normal = u * cos(angle) + v * sin(angle)
        return surface.sweep_angle < 360 or abs(normal.dot(camera.toward_viewer)) < 1e-10

    top_end = camera.project(surface.point(end * 180 / pi, surface.height))
    if vertical_boundary(end):
        outline.line_to(top_end)
    else:
        outline.move_to(top_end)
    _arc(outline, surface, camera, end, start, surface.height)
    if vertical_boundary(start):
        outline.line_to(bottom_start)
    return make_entity(
        make_group(
            (
                fill,
                make_entity(
                    outline,
                    Style(
                        fill=None,
                        stroke=surface.stroke,
                        line_width=surface.line_width,
                        line_join="round",
                    ),
                ),
            )
        )
    )


def project_cylinder_surface(surface: CylinderSurface, camera: OrthographicCamera) -> Entity:
    """Split at exact orthographic silhouettes and paint the far branch first."""
    _, u, v = _basis(surface.axis, surface.radial)
    start = radians(surface.start_angle % 360)
    end = start + radians(surface.sweep_angle)
    phase = atan2(camera.toward_viewer.dot(v), camera.toward_viewer.dot(u))
    cuts = [start, end]
    for i in range(-4, 7):
        angle = phase + pi / 2 + i * pi
        if start + 1e-10 < angle < end - 1e-10:
            cuts.append(angle)
    cuts.sort()
    spans = list(zip(cuts[:-1], cuts[1:], strict=True))
    spans.sort(key=lambda ab: camera.depth(surface.point((ab[0] + ab[1]) * 90 / pi)))
    drawings = tuple(_patch(surface, camera, a, b) for a, b in spans)
    return make_entity(make_group(drawings))


def project_annular_cylinder(washer: AnnularCylinder, camera: OrthographicCamera) -> Entity:
    """Paint the visible inner wall, outer wall and facing annular cap."""
    axis = washer.axis.normalized()
    reference = Vector3D(1, 0, 0) if abs(axis.x) < 0.9 else Vector3D(0, 1, 0)
    radial = (reference + axis * -reference.dot(axis)).normalized()
    side = axis.cross(radial)
    viewer = camera.toward_viewer
    phase = atan2(viewer.dot(side), viewer.dot(radial)) * 180 / pi
    outer = CylinderSurface(
        base=washer.base,
        radius=washer.outer_radius,
        height=washer.height,
        axis=axis,
        radial=radial,
        start_angle=phase - 90,
        sweep_angle=180,
        color=washer.color,
        stroke=washer.stroke,
        line_width=washer.line_width,
    )
    inner = replace(outer, radius=washer.inner_radius, start_angle=phase + 90)
    drawings: list[Entity] = []
    if abs(axis.dot(viewer)) < 1 - 1e-10:
        drawings.extend(
            (project_cylinder_surface(inner, camera), project_cylinder_surface(outer, camera))
        )
    if abs(axis.dot(viewer)) > 1e-10:
        height = washer.height if axis.dot(viewer) >= 0 else 0
        cap = Path().move_to(camera.project(outer.point(0, height)))
        _arc(cap, outer, camera, 0, 2 * pi, height)
        cap.close().move_to(camera.project(inner.point(0, height)))
        _arc(cap, inner, camera, 0, -2 * pi, height)
        cap.close()
        drawings.append(
            make_entity(
                cap, Style(fill=washer.color, stroke=washer.stroke, line_width=washer.line_width)
            )
        )
    return make_entity(make_group(tuple(drawings)))
