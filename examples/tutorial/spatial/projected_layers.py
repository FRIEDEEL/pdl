"""Separate projections share world coordinates and follow explicit Canvas order."""

from pdl import (
    Canvas,
    Color,
    Cylinder,
    CylinderSurface,
    Group,
    OrthographicCamera,
    Point3D,
    Scene3D,
    Style,
    Text,
    Transform,
    Vector3D,
)

# tutorial-start
camera = OrthographicCamera(0, 20)
material = CylinderSurface(
    base=Point3D(0, 0, -18),
    radius=16,
    height=36,
    start_angle=90,
    sweep_angle=180,
    color=Color(0.72, 0.84, 0.9),
)
probe = Cylinder(
    base=Point3D(0, 0, -8),
    radius=1.5,
    height=36,
    axis=Vector3D(0, 0, 1),
    color=Color(0.9, 0.38, 0.16),
)
material_2d = Scene3D((material,), camera, sort_faces=False).project()
probe_2d = Scene3D((probe,), camera, light=None, sort_faces=False).project()

canvas = Canvas(150, 85)
# Keep the unmodified background beside the assembled illustration.
canvas.draw(material_2d.copy().apply_transform(Transform.translate(38, 38)))
assembly = Group()
assembly.add(material_2d)
assembly.add(probe_2d)  # Later 2D drawing covers the material, regardless of depth.
# A 2D annotation uses the same snapshot to project the world-space probe tip.
probe_tip = material_2d.point(Point3D(0, 0, 28))
assembly.add(
    Text("probe", position=(probe_tip.x + 3, probe_tip.y), size=10).set_style(
        Style(fill=Color(0.65, 0.22, 0.08), stroke=None)
    )
)
canvas.draw(assembly.copy().apply_transform(Transform.translate(112, 38)))
# tutorial-end

if __name__ == "__main__":
    from examples._shared import export

    export(canvas, __file__, tikz_mode="pdf")
