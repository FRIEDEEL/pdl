"""An open half-cylinder projected into ordinary 2D authoring."""

from pdl import (
    Canvas,
    Color,
    CylinderSurface,
    Drawing,
    OrthographicCamera,
    Point3D,
    Scene3D,
    Transform,
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
material_2d = Scene3D((material,), camera, sort_faces=False).project()
canvas = Canvas(75, 70)
canvas.draw(Drawing(material_2d, transform=Transform.translate(37, 34)))
# tutorial-end

if __name__ == "__main__":
    from examples._shared import export

    export(canvas, __file__, tikz_mode="pdf")
