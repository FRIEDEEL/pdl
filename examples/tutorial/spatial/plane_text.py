"""Compare a flat chart and its inclined projection with native text."""

# tutorial-start
from pdl import (
    Canvas,
    Color,
    Drawing,
    Group,
    Node,
    OrthographicCamera,
    Plane3D,
    Rectangle,
    Scene3D,
    Style,
    Text,
    Transform,
    Transform3D,
    Vector3D,
)

panel = Rectangle((-20, -10), 40, 20)
label = Node(Text("Plane 123", size=17), padding=(0, 0), style=Style(stroke=None))
artwork = Group((Drawing(panel, Style(fill=Color(0.78, 0.9, 1), line_width=0.3)), Drawing(label)))
flat = Plane3D()
tilted = flat.transformed(Transform3D.rotate(25) @ Transform3D.rotate(55, Vector3D(1, 0, 0)))
camera = OrthographicCamera(-90, 90)
first = Scene3D((flat.place(artwork),), camera=camera, visibility="centroid").project()
second = Scene3D((tilted.place(artwork),), camera=camera, visibility="centroid").project()

canvas = Canvas(125, 50)
canvas.draw(Drawing(first, transform=Transform.translate(30, 26)))
canvas.draw(Drawing(second, transform=Transform.translate(91, 26)))
canvas.draw(Text("Flat chart", position=(15, 5), size=10))
canvas.draw(Text("Inclined chart", position=(76, 5), size=10))
# tutorial-end

if __name__ == "__main__":
    from examples._shared import export

    export(canvas, __file__, tikz_mode="pdf")
