"""A 2D drawing on an inclined plane and nested 3D frame conversion."""

from examples._shared import export, latin_font
from pdl import (
    Canvas,
    Circle,
    Color,
    CoordinateSystem3D,
    DirectionalLight,
    Group,
    Line,
    OrthographicCamera,
    Plane3D,
    Point3D,
    Rectangle,
    Scene3D,
    Style,
    Text,
    Transform3D,
    Vector3D,
)
from pdl.author.entity.factories import as_entity


def example() -> Canvas:
    world = CoordinateSystem3D()
    local = world.child(Transform3D.rotate(25, Vector3D(0, 1, 0)))
    child = local.child(Transform3D.translate(8, 6, 0))
    origin = local.convert_point(Point3D(0, 0, 0), world)
    plane = Plane3D(
        origin,
        local.convert_vector(Vector3D(1, 0, 0), world),
        local.convert_vector(Vector3D(0, 1, 0), world),
    )
    light = DirectionalLight(Vector3D(-1, 1, -2))
    fill = light.shade(Color(0.65, 0.83, 0.95), plane.normal)
    panel = Rectangle((-20, -15), 40, 30)
    marker = Circle((8, 6), 4)
    artwork = Group(
        as_entity(panel, Style(fill=fill, line_width=0.35)),
        as_entity(marker, Style(fill=Color(0.95, 0.57, 0.24), line_width=0.3)),
        as_entity(Line((-20, 0), (20, 0)), Style(line_width=0.2)),
        as_entity(Line((0, -15), (0, 15)), Style(line_width=0.2)),
    )
    scene = Scene3D(
        (plane.place(artwork),), camera=OrthographicCamera(35, 35), visibility="centroid"
    )
    marker_world = child.convert_point(Point3D(0, 0, 0), world)
    expected = scene.camera.project(marker_world)
    annotation = Text(
        "Frame origin at (8, 6, 0)",
        font=latin_font(),
        position=(28, -6),
        size=10,
    )
    leader = Line((expected.x + 4, expected.y), (27, -6))
    title = Text("2D artwork on a 3D plane", font=latin_font(), position=(-30, 30), size=14)
    canvas = Canvas(120, 85, mode="fit", padding=8)
    canvas.draw(scene.project())
    canvas.draw(leader, Style(stroke=Color(0.35, 0.35, 0.35), line_width=0.2))
    canvas.draw(annotation, Style(stroke=None, fill=Color(0.2, 0.2, 0.2)))
    canvas.draw(title, Style(stroke=None, fill=Color(0.2, 0.2, 0.2)))
    return canvas


if __name__ == "__main__":
    export(example(), __file__, tikz_mode="pdf")
