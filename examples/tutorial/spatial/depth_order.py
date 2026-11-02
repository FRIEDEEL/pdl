"""Transparent back faces and explicit back-to-front order overrides."""

from dataclasses import replace

from pdl import (
    Canvas,
    Color,
    PerspectiveCamera,
    Plane3D,
    Point3D,
    Scene3D,
    Style,
    Translation,
    Vector3D,
    rectangle,
    regular_polyhedron,
    text,
)

# tutorial-start
camera = PerspectiveCamera(0, 0, distance=80, focal_length=80)
blue = Style(fill=Color(0.15, 0.45, 0.95), opacity=0.55, line_width=0.3)
orange = Style(fill=Color(1, 0.4, 0.1), opacity=0.55, line_width=0.3)
far = Plane3D(Point3D(-8, -4, 0), Vector3D(0, 1, 0), Vector3D(0, 0, 1))
near = Plane3D(Point3D(8, 4, 0), Vector3D(0, 1, 0), Vector3D(0, 0, 1))
objects = (
    near.place(rectangle((-15, -13), 30, 26), orange),
    far.place(rectangle((-15, -13), 30, 26), blue),
)
automatic = Scene3D(objects, camera, light=None, visibility="centroid").project()
manual = Scene3D(objects, camera, light=None, sort_faces=False).project()
# Or permute the current projected paint list; source queries remain unchanged.
restored = manual.reordered((1, 0))

cube = regular_polyhedron("cube", radius=22)
transparent = replace(cube, opacity=0.25)
view = PerspectiveCamera(28, 22, distance=90, focal_length=90)
opaque_view = Scene3D((cube,), view).project()
transparent_view = Scene3D((transparent,), view).project()

canvas = Canvas(150, 135)
for x, image in ((37, opaque_view), (112, transparent_view)):
    canvas.draw(image.copy().apply_transform(Translation(x, 103)))
for x, image in ((37, automatic), (112, manual)):
    canvas.draw(image.copy().apply_transform(Translation(x, 38)))
ink = Style(stroke=None, fill=Color(0.12, 0.18, 0.25))
for x, title in ((12, "Opaque reference"), (87, "Opacity 0.25 / back faces kept")):
    canvas.draw(text(title, position=(x, 129), size=10), ink)
for x, title in ((9, "Automatic: far, then near"), (83, "Manual: near, then far")):
    canvas.draw(text(title, position=(x, 63), size=10), ink)
canvas.draw(text("Transparent overlap changes with paint order", position=(25, 10), size=11), ink)
# tutorial-end

if __name__ == "__main__":
    from examples._shared import export

    export(canvas, __file__, tikz_mode="pdf")
