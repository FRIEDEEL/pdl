"""Project first, then describe an ordinary 2D legend."""

# tutorial-start
from pdl import (
    Canvas,
    Color,
    Drawing,
    Group,
    Line,
    OrthographicCamera,
    Scene3D,
    Style,
    Text,
    Transform,
    regular_polyhedron,
)

solid = regular_polyhedron("cube", radius=14)
scene = Scene3D((solid,), camera=OrthographicCamera(30, 25))
projected = scene.project()

# These are fixed coordinates in the projected drawing's local 2D space.
corner = projected.vertex(0, 7)
leader = Line(corner, (25, 16))
legend = Text("A projected vertex", position=(26, 15), size=10)
component = Group(
    (
        Drawing(projected),
        Drawing(leader, Style(stroke=Color(0.3, 0.3, 0.3), line_width=0.25)),
        Drawing(legend),
    )
)

canvas = Canvas(105, 60, mode="fit", padding=6)
canvas.draw(Drawing(component, transform=Transform.rotate(-8)))
# tutorial-end

if __name__ == "__main__":
    from examples._shared import export

    export(canvas, __file__, tikz_mode="pdf")
