"""Compare orthographic reference, perspective plane artwork, and a D10."""

from examples.spatial.d10 import numbered_die
from pdl import (
    Canvas,
    Color,
    Drawing,
    Group,
    Line,
    Node,
    OrthographicCamera,
    PerspectiveCamera,
    Plane3D,
    Rectangle,
    Scene3D,
    Style,
    Text,
    Transform,
    Vector3D,
)

# tutorial-start
plane = Plane3D(u=Vector3D(0.8, 1, 0), v=Vector3D(0, 0, 1))
artwork = Group(
    (
        Drawing(Rectangle((-22, -12), 44, 24), Style(fill=Color(0.65, 0.84, 1), line_width=0.3)),
        Drawing(Node(Text("Plane 123", size=16), style=Style(stroke=None))),
        Drawing(Line((-18, -8), (18, -8)), Style(line_width=0.3)),
    )
)
ortho = OrthographicCamera(0, 0)
camera = PerspectiveCamera(0, 0, distance=55, focal_length=55)
reference = Scene3D((plane.place(artwork),), ortho).project()
projected = Scene3D((plane.place(artwork),), camera).project()

die = numbered_die()
die_ortho = Scene3D((die,), OrthographicCamera(28, 22)).project()
die_perspective = Scene3D((die,), PerspectiveCamera(28, 22, distance=90, focal_length=90)).project()

canvas = Canvas(160, 145)
for x, panel in ((40, reference), (120, projected)):
    canvas.draw(Drawing(panel, transform=Transform.translate(x, 110)))
for x, solid in ((40, die_ortho), (120, die_perspective)):
    canvas.draw(Drawing(solid, transform=Transform.translate(x, 43)))
ink = Style(stroke=None, fill=Color(0.12, 0.18, 0.25))
for x, title in ((12, "Orthographic reference"), (94, "Perspective")):
    canvas.draw(Text(title, position=(x, 135), size=12), ink)
canvas.draw(
    Text("Same chart, same artwork; target-plane scale = 1", position=(18, 87), size=10), ink
)
canvas.draw(Text("D10 / native text", position=(18, 5), size=10), ink)
canvas.draw(Text("D10 / vector outlines", position=(95, 5), size=10), ink)
# tutorial-end

if __name__ == "__main__":
    from examples._shared import export

    export(canvas, __file__, tikz_mode="pdf")
