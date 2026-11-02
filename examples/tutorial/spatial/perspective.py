"""Compare orthographic reference, perspective plane artwork, and a D10."""

from examples.spatial.d10 import numbered_die
from pdl import Canvas, Color, Group, Style, line, rectangle, text
from pdl.author.transform import Translation
from pdl.extensions.diagram import Node
from pdl.extensions.spatial import OrthographicCamera, PerspectiveCamera, Plane3D, Scene3D, Vector3D

# tutorial-start
plane = Plane3D(u=Vector3D(0.8, 1, 0), v=Vector3D(0, 0, 1))
artwork = Group(
    rectangle((-22, -12), 44, 24).set_style(Style(fill=Color(0.65, 0.84, 1), line_width=0.3)),
    Node(text("Plane 123", size=16), style=Style(stroke=None)),
    line((-18, -8), (18, -8)).set_style(Style(line_width=0.3)),
)
ortho = OrthographicCamera(0, 0)
camera = PerspectiveCamera(0, 0, distance=55, focal_length=55)
reference = Scene3D((plane.place(artwork),), ortho, visibility="centroid").project()
projected = Scene3D((plane.place(artwork),), camera, visibility="centroid").project()

die = numbered_die()
die_ortho = Scene3D((die,), OrthographicCamera(28, 22), visibility="centroid").project()
die_perspective = Scene3D(
    (die,), PerspectiveCamera(28, 22, distance=90, focal_length=90), visibility="centroid"
).project()

canvas = Canvas(160, 145)
for x, panel in ((40, reference), (120, projected)):
    canvas.draw(panel.copy().apply_transform(Translation(x, 110)))
for x, solid in ((40, die_ortho), (120, die_perspective)):
    canvas.draw(solid.copy().apply_transform(Translation(x, 43)))
ink = Style(stroke=None, fill=Color(0.12, 0.18, 0.25))
for x, title in ((12, "Orthographic reference"), (94, "Perspective")):
    canvas.draw(text(title, position=(x, 135), size=12), ink)
canvas.draw(
    text("Same chart, same artwork; target-plane scale = 1", position=(18, 87), size=10), ink
)
canvas.draw(text("D10 / orthographic", position=(18, 5), size=10), ink)
canvas.draw(text("D10 / perspective", position=(95, 5), size=10), ink)
# tutorial-end

if __name__ == "__main__":
    from examples._shared import export

    export(canvas, __file__, tikz_mode="pdf")
