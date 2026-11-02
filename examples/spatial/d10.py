"""A ten-faced die with vector face artwork and independent 2D annotations.

Run: uv run python -m examples.spatial.d10
"""

from math import cos, pi, sin

from examples._shared import export, latin_font
from pdl import (
    Canvas,
    Color,
    DirectionalLight,
    Group,
    Line,
    Node,
    OrthographicCamera,
    Point3D,
    Polyhedron,
    Scene3D,
    Style,
    Text,
    Translation,
    Vector3D,
)
from pdl.author.entity.factories import as_entity

DIE_COLOR = Color(0.12, 0.48, 0.7)
WHITE = Color(1, 1, 1)
INK = Style(stroke=None, fill=Color(0.1, 0.17, 0.23))


def die_geometry() -> Polyhedron:
    """Build a pentagonal trapezohedron as an example, not a library primitive."""
    radius, pole = 22.0, 30.0
    ring_height = pole * (1 - cos(pi / 5)) / (1 + cos(pi / 5))
    vertices = tuple(
        Point3D(
            radius * cos(i * pi / 5),
            radius * sin(i * pi / 5),
            ring_height if i % 2 == 0 else -ring_height,
        )
        for i in range(10)
    )
    vertices += (Point3D(0, 0, pole), Point3D(0, 0, -pole))
    faces: list[tuple[int, ...]] = []
    for i in range(10):
        face = (10 if i % 2 == 0 else 11, i, (i + 1) % 10, (i + 2) % 10)
        a, b, c = (vertices[j] for j in face[:3])
        normal = (b - a).cross(c - a)
        if normal.dot(a - Point3D(0, 0, 0)) < 0:
            face = tuple(reversed(face))
        faces.append(face)
    return Polyhedron(
        vertices, tuple(faces), color=DIE_COLOR, stroke=Color(0.04, 0.16, 0.22), line_width=0.35
    )


def numbered_die() -> Polyhedron:
    """Generate plane-local number artwork; nothing is rasterized or measured here."""
    die = die_geometry()
    font = latin_font()
    for i in range(10):
        number = Node(
            Text(str(i + 1), font=font, size=21),
            padding=(0, 0),
            style=Style(stroke=None),
            text_style=Style(stroke=None, fill=WHITE),
        )
        marks = [as_entity(number)]
        if i + 1 in (6, 9):
            marks.append(
                as_entity(Line((-1.7, -4.5), (1.7, -4.5)), Style(stroke=WHITE, line_width=0.35))
            )
        die = die.with_face_artwork(i, Group(*tuple(marks)))
    return die


def example() -> Canvas:
    die = numbered_die()
    light = DirectionalLight(Vector3D(-1, -2, -3), ambient=0.38)
    front = Scene3D((die,), OrthographicCamera(28, 22), light, visibility="centroid").project()
    back = Scene3D((die,), OrthographicCamera(208, -22), light, visibility="centroid").project()

    # The annotation is ordinary 2D authoring, created after projection.
    face = 0
    point = front.face_center(0, face)
    label = Node(
        Text("Face 1", font=latin_font(), size=10),
        position=(39, 12),
        padding=(1.5, 1),
        style=Style(stroke=None, fill=Color(0.92, 0.95, 0.97)),
    )
    leader = Line((point.x + 3, point.y), (34, 12))
    front_with_legend = Group(
        as_entity(front),
        as_entity(leader, Style(stroke=Color(0.35, 0.4, 0.45), line_width=0.25)),
        as_entity(label),
    )
    first = as_entity(front_with_legend, transform=Translation(42, 51))
    second = as_entity(back, transform=Translation(145, 51))
    title = Text(
        "D10: planar artwork, then a 2D legend", font=latin_font(), position=(8, 101), size=18
    )
    subtitle = Text(
        "Ten kite faces / face numbers / opposite orthographic views",
        font=latin_font(),
        position=(8, 92),
        size=10,
    )
    notes = (
        Text("Front view + 2D annotation", font=latin_font(), position=(12, 12), size=10),
        Text("Opposite view", font=latin_font(), position=(122, 12), size=10),
        Text(
            "Numbers 1-10 are example artwork; no canonical dice numbering is implied.",
            font=latin_font(),
            position=(8, 4),
            size=8,
        ),
    )
    canvas = Canvas(200, 110)
    canvas.draw(first)
    canvas.draw(second)
    canvas.draw(title, INK)
    canvas.draw(subtitle, INK)
    for note in notes:
        canvas.draw(note, INK)
    return canvas


if __name__ == "__main__":
    export(example(), __file__, tikz_mode="pdf")
