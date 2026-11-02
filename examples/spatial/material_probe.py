"""A cylindrical material cutaway assembled from independent projected layers.

Run: uv run python -m examples.spatial.material_probe
This is a fixed-view illustration, not a boolean section or depth-buffer scene.
"""

from dataclasses import replace

from examples._shared import export, latin_font
from pdl import Canvas, Color, Group, Style, line, text
from pdl.author.entity.factories import as_entity
from pdl.author.geometry import Path as PathGeometry
from pdl.author.geometry.shapes import Arc as ArcGeometry
from pdl.author.transform import Translation
from pdl.extensions.spatial import (
    AnnularCylinder,
    Cylinder,
    CylinderSurface,
    OrthographicCamera,
    Plane3D,
    Point3D,
    ProjectedScene,
    Scene3D,
    Transform3D,
    Vector3D,
)

MATERIAL = Color(0.72, 0.84, 0.9)
PROBE = Color(0.91, 0.4, 0.16)
INK = Color(0.12, 0.2, 0.27)
CAMERA = OrthographicCamera(0, 22)


def make_material() -> CylinderSurface:
    """Keep the rear half of the material wall, opening toward world +x."""
    return CylinderSurface(
        base=Point3D(0, 0, -22),
        radius=20,
        height=44,
        start_angle=90,
        sweep_angle=180,
        color=MATERIAL,
        stroke=INK,
    )


def make_probe() -> Cylinder:
    """Place a narrow probe on the material axis; it extends above the opening."""
    return Cylinder(base=Point3D(0, 0, -10), radius=1.6, height=46, color=PROBE, stroke=INK)


def project_material(material: CylinderSurface) -> ProjectedScene:
    return Scene3D((material,), CAMERA, light=None, sort_faces=False).project()


def make_cutaway(material: CylinderSurface, probe: Cylinder, *, label: bool = True) -> Group:
    """Compose named 2D layers in an intentional back-to-front order."""
    background = project_material(material)
    interior_floor = (
        PathGeometry()
        .move_to((0, 0))
        .arc(ArcGeometry((0, 0), material.radius, material.radius, 90, 180))
        .close()
    )
    floor = Plane3D(origin=material.base)
    floor_2d = Scene3D(
        (
            floor.place(
                interior_floor, Style(fill=Color(0.86, 0.91, 0.94), stroke=INK, line_width=0.25)
            ),
        ),
        CAMERA,
        sort_faces=False,
    ).project()
    probe_2d = Scene3D((probe,), CAMERA, light=None, sort_faces=False).project()
    assembly = Group()
    assembly.add(background)
    assembly.add(floor_2d)
    assembly.add(probe_2d)
    if label:
        tip = background.point(probe.base + probe.axis.normalized() * probe.height)
        assembly.add(
            line((tip.x + 1, tip.y - 1), (tip.x + 13, tip.y + 3)).set_style(
                Style(stroke=PROBE, line_width=0.25)
            )
        )
        assembly.add(
            text("probe", position=(tip.x + 14, tip.y + 2), size=10).set_style(
                Style(fill=INK, stroke=None)
            )
        )
    return assembly


def example() -> Canvas:
    """Compare the background, assembled cutaway and a 3D probe edit."""
    material, probe = make_material(), make_probe()
    canvas = Canvas(240, 125)
    font = latin_font()
    ink = Style(fill=INK, stroke=None)
    canvas.draw(
        text(
            "Cylindrical material / independently projected layers",
            font=font,
            position=(9, 113),
            size=16,
        ),
        ink,
    )
    reference = replace(material, color=Color(0.86, 0.91, 0.94))
    canvas.draw(as_entity(project_material(reference), transform=Translation(40, 52)))
    canvas.draw(as_entity(make_cutaway(material, probe), transform=Translation(115, 52)))
    moved_probe = replace(probe, base=Point3D(3, 4, -10), axis=Vector3D(0, 0.16, 1))
    canvas.draw(as_entity(make_cutaway(material, moved_probe), transform=Translation(192, 52)))
    for x, title in (
        (13, "1. Material background"),
        (88, "2. Add interior + probe"),
        (166, "3. Reposition probe in 3D"),
    ):
        canvas.draw(text(title, font=font, position=(x, 18), size=10), ink)
    canvas.draw(
        text(
            "Same camera + shared world frame; Canvas order controls overlap.",
            font=font,
            position=(14, 7),
            size=10,
        ),
        ink,
    )
    return canvas


def views() -> Canvas:
    """Inspect washers and open surfaces from above, below, side and along axis."""
    canvas = Canvas(235, 135)
    ink = Style(fill=INK, stroke=None)
    washer = AnnularCylinder(outer_radius=17, inner_radius=10, height=8, color=MATERIAL, stroke=INK)
    for i, (title, camera) in enumerate(
        (
            ("Above", OrthographicCamera(15, 35)),
            ("Below", OrthographicCamera(15, -35)),
            ("Side", OrthographicCamera(0, 0)),
            ("Along axis", OrthographicCamera(0, 90)),
        )
    ):
        x = 30 + 58 * i
        canvas.draw(text(title, position=(x - 15, 121), size=11), ink)
        # A colored line behind the bore makes accidental hole filling visible.
        canvas.draw(line((x - 22, 89), (x + 22, 89)), Style(stroke=PROBE, line_width=1))
        flat = Scene3D((washer,), camera, sort_faces=False).project()
        canvas.draw(as_entity(flat, transform=Translation(x, 87)))
        surface = make_material().transformed(Transform3D.scale(0.65))
        flat_surface = Scene3D((surface,), camera, sort_faces=False).project()
        canvas.draw(as_entity(flat_surface, transform=Translation(x, 35)))
    return canvas


if __name__ == "__main__":
    from examples._shared import output_base

    export(example(), __file__, tikz_mode="pdf")
    base = output_base(__file__).with_name("material_probe-views")
    views().save(base.with_suffix(".svg"))
    views().save(base.with_suffix(".tex"), backend="tikz", tikz_mode="pdf")
