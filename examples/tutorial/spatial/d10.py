"""Attach face artwork before projection; add a 2D legend afterward."""

from examples.spatial.d10 import die_geometry

# tutorial-start
from pdl import (
    Canvas,
    Color,
    Group,
    Line,
    Node,
    OrthographicCamera,
    Scene3D,
    Style,
    Text,
)

# Geometry construction is linked separately: 12 vertices and 10 kite loops.
die = die_geometry()
for face_index in range(10):
    number = Node(
        Text(str(face_index + 1), size=18),
        padding=(0, 0),
        style=Style(stroke=None),
        text_style=Style(stroke=None, fill=Color(1, 1, 1)),
    )
    die = die.with_face_artwork(face_index, number)

projected = Scene3D((die,), camera=OrthographicCamera(28, 22), visibility="centroid").project()
center = projected.face_center(0, 0)
leader = Line((center.x + 3, center.y), (38, 14))
legend = Text("Face 1: a 2D legend", position=(40, 13), size=10)
component = Group(
    (projected.copy(), leader.copy().set_style(Style(line_width=0.25)), legend.copy())
)

canvas = Canvas(120, 85, mode="fit", padding=7)
canvas.draw(component)
# tutorial-end

if __name__ == "__main__":
    from examples._shared import export

    export(canvas, __file__, tikz_mode="pdf")
