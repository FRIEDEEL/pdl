"""Two intersecting faces, with a centroid reference beside BSP visibility."""

from dataclasses import replace

from pdl import Canvas, Color, Style, text
from pdl.author.transform import Translation
from pdl.extensions.spatial import PerspectiveCamera, Point3D, Polyhedron, Scene3D

# tutorial-start
camera = PerspectiveCamera(0, 0, distance=100, focal_length=100)
red_panel = Polyhedron(
    (Point3D(-20, -30, -20), Point3D(20, 30, -20), Point3D(20, 30, 20), Point3D(-20, -30, 20)),
    ((0, 1, 2, 3),),
    color=Color(0.9, 0.35, 0.24),
    line_width=0.25,
)
blue_panel = Polyhedron(
    (Point3D(20, -30, -20), Point3D(-20, 30, -20), Point3D(-20, 30, 20), Point3D(20, -30, 20)),
    ((0, 1, 2, 3),),
    color=Color(0.15, 0.57, 0.78),
    line_width=0.25,
)
scene = Scene3D((red_panel, blue_panel), camera, light=None)
projected = scene.project()  # auto selects BSP for polygon-only scenes
reference = replace(scene, visibility="centroid").project()
assert projected.visibility == "bsp"
assert set(projected.source_faces) == {(0, 0), (1, 0)}

canvas = Canvas(180, 95)
canvas.draw(reference.copy().apply_transform(Translation(45, 45)))
canvas.draw(projected.copy().apply_transform(Translation(135, 45)))
ink = Style(stroke=None, fill=Color(0.12, 0.18, 0.25))
for x, title in ((12, "Centroid reference"), (103, "BSP: split and order")):
    canvas.draw(text(title, position=(x, 85), size=12), ink)
canvas.draw(
    text("Same faces / perspective / no extra cut-edge strokes", position=(25, 8), size=10), ink
)
# tutorial-end

if __name__ == "__main__":
    from examples._shared import export

    export(canvas, __file__, tikz_mode="pdf")
