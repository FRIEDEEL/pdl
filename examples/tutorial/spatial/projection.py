"""Project first, then describe an ordinary 2D legend."""

# tutorial-start
from pdl import (
    Canvas,
    Color,
    Group,
    Line,
    OrthographicCamera,
    Rotation,
    Scene3D,
    Style,
    Text,
    regular_polyhedron,
)

solid = regular_polyhedron("cube", radius=14)
scene = Scene3D((solid,), camera=OrthographicCamera(30, 25))
projected = scene.project()

# These are fixed coordinates in the projected drawing's authoring 2D world.
corner = projected.vertex(0, 7)
leader = Line(corner, (25, 16))
legend = Text("A projected vertex", position=(26, 15), size=10)
component = Group(
    projected.copy(),
    leader.copy().set_style(Style(stroke=Color(0.3, 0.3, 0.3), line_width=0.25)),
    legend.copy(),
)

canvas = Canvas(105, 60, mode="fit", padding=6)
canvas.draw(component.copy().apply_transform(Rotation(-8)))
# tutorial-end

if __name__ == "__main__":
    from examples._shared import export

    export(canvas, __file__, tikz_mode="pdf")
