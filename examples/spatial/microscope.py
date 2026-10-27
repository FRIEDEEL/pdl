"""A named-part microscope assembly and exploded vector design study.

Run: uv run python -m examples.spatial.microscope
Dimensions are illustrative millimeters, not manufacturing specifications.
Each Part owns local solids, an assembly origin and a separate explosion offset.
"""

from dataclasses import dataclass, replace
from math import cos, pi, sin

from examples._shared import export, latin_font
from pdl import (
    Canvas,
    Color,
    Cylinder,
    DirectionalLight,
    Drawing,
    Line,
    OrthographicCamera,
    Point3D,
    Polyhedron,
    Rectangle,
    Scene3D,
    Style,
    Text,
    Transform,
    Transform3D,
    Vector3D,
)

IVORY = Color(0.84, 0.87, 0.86)
DARK = Color(0.16, 0.22, 0.27)
SILVER = Color(0.69, 0.77, 0.81)
BLUE = Color(0.13, 0.54, 0.65)
GOLD = Color(0.92, 0.64, 0.25)
INK = Color(0.12, 0.20, 0.25)
CAMERA = OrthographicCamera(235, 22)
LIGHT = DirectionalLight(Vector3D(0.5, 1, -2), ambient=0.48)
Solid = Polyhedron | Cylinder


def prism(outline: tuple[tuple[float, float], ...], depth: float, color: Color) -> Polyhedron:
    """Extrude a counterclockwise x/z outline along y, centered on y=0."""
    count = len(outline)
    vertices = tuple(Point3D(x, y, z) for y in (-depth / 2, depth / 2) for x, z in outline)
    faces = (tuple(range(count)), tuple(reversed(range(count, 2 * count))))
    faces += tuple((i, i + count, (i + 1) % count + count, (i + 1) % count) for i in range(count))
    return Polyhedron(vertices, faces, color=color, stroke=INK, line_width=0.16)


def block(width: float, depth: float, height: float, color: Color) -> Polyhedron:
    """Build a centered rectangular part resting on z=0."""
    return prism(
        ((-width / 2, 0), (width / 2, 0), (width / 2, height), (-width / 2, height)), depth, color
    )


def barrel(
    radius: float,
    height: float,
    z: float,
    color: Color,
    x: float = 0,
    y: float = 0,
    axis: Vector3D = Vector3D(0, 0, 1),
) -> Cylinder:
    """Make an axial component in its parent part's local coordinates."""
    return Cylinder(Point3D(x, y, z), radius, height, axis, color, INK, 0.14)


@dataclass(frozen=True)
class Part:
    """A named subassembly with local geometry and explicit assembly placement."""

    name: str
    solids: tuple[Solid, ...]
    origin: Point3D
    explosion: Vector3D = Vector3D(0, 0, 0)

    def placed(self, exploded: bool) -> tuple[Solid, ...]:
        """Translate all members together without changing the original assembly."""
        origin = self.origin + self.explosion if exploded else self.origin
        shift = Vector3D(origin.x, origin.y, origin.z)
        transform = Transform3D.translate(origin.x, origin.y, origin.z)
        return tuple(
            s.transformed(transform)
            if isinstance(s, Polyhedron)
            else replace(s, base=s.base + shift)
            for s in self.solids
        )


def microscope_parts() -> tuple[Part, ...]:
    """Describe the instrument as readable, independently movable subassemblies."""
    base = Part(
        "Base",
        (prism(((-34, 0), (30, 0), (34, 4), (28, 10), (-28, 10), (-35, 5)), 47, IVORY),),
        Point3D(0, 0, 0),
    )
    arm = Part(
        "Support arm",
        (
            prism(
                ((14, 9), (27, 9), (27, 92), (17, 110), (-7, 110), (-7, 100), (10, 100), (15, 88)),
                16,
                IVORY,
            ),
        ),
        Point3D(0, 9, 0),
    )
    illuminator = Part(
        "Illuminator",
        (barrel(11, 5, 0, DARK), barrel(8.5, 1.2, 5, BLUE)),
        Point3D(-12, -3, 10),
        Vector3D(-9, 0, 0),
    )
    condenser = Part(
        "Condenser",
        (barrel(8, 5, 0, SILVER), barrel(11, 2, 5, DARK), barrel(6, 3, 7, BLUE)),
        Point3D(-12, -3, 28),
        Vector3D(-5, 0, -5),
    )
    stage = Part(
        "Mechanical stage", (block(45, 37, 4, DARK),), Point3D(-8, -3, 45), Vector3D(-9, -2, 0)
    )
    slide = Part(
        "Specimen slide",
        (block(25, 10, 0.8, Color(0.65, 0.84, 0.85)), barrel(2.3, 0.3, 0.8, GOLD, x=-4)),
        Point3D(-12, -5, 49.2),
        Vector3D(-18, -5, 10),
    )
    slide_clips = Part(
        "Slide clips",
        tuple(
            block(3, 13, 0.8, SILVER).transformed(Transform3D.translate(x, 0, 0)) for x in (-17, 16)
        ),
        Point3D(-8, -3, 49),
        Vector3D(-9, -2, 0),
    )
    nosepiece = Part(
        "Revolving nosepiece",
        (barrel(13, 4, 0, DARK), barrel(9, 2, 4, SILVER)),
        Point3D(-12, -3, 79),
        Vector3D(-4, 0, 21),
    )
    objectives: list[Part] = []
    for index, (angle, length, band) in enumerate(
        ((210, 17, BLUE), (330, 13, GOLD), (90, 10, Color(0.7, 0.3, 0.3)))
    ):
        x, y = 7 * cos(angle * pi / 180), 7 * sin(angle * pi / 180)
        objective = Part(
            f"Objective {index + 1}",
            (
                barrel(3.8, 3, 0, SILVER),
                barrel(3.8, length - 4.7, 4.7, SILVER),
                barrel(4, 1.7, 3, band),
                barrel(2.5, 1.5, -1.5, DARK),
            ),
            Point3D(-12 + x, -3 + y, 79 - length),
            Vector3D(-4 + x * 0.5, y * 0.5, 13),
        )
        objectives.append(objective)
    body_tube = Part(
        "Body tube",
        (barrel(8, 28, 0, IVORY), barrel(8.8, 3, 26, DARK)),
        Point3D(-12, -3, 85),
        Vector3D(0, 0, 31),
    )
    eyepiece = Part(
        "Eyepiece",
        (barrel(5.5, 10, 0, SILVER), barrel(7.5, 9, 10, DARK), barrel(5.5, 0.7, 19, BLUE)),
        Point3D(-12, -3, 113),
        Vector3D(0, 0, 43),
    )
    coarse_focus = Part(
        "Coarse focus",
        (
            barrel(10, 8, 0, DARK, axis=Vector3D(0, -1, 0)),
            barrel(8.7, 1, 0, SILVER, y=-8, axis=Vector3D(0, -1, 0)),
        ),
        Point3D(21, -1, 78),
        Vector3D(13, -9, 0),
    )
    fine_focus = Part(
        "Fine focus",
        (
            barrel(4.4, 4, 0, DARK, axis=Vector3D(0, -1, 0)),
            barrel(3.2, 0.6, 0, BLUE, y=-4, axis=Vector3D(0, -1, 0)),
        ),
        Point3D(21, -10, 78),
        Vector3D(13, -14, 0),
    )
    return (
        base,
        arm,
        illuminator,
        condenser,
        stage,
        slide,
        slide_clips,
        nosepiece,
        *objectives,
        body_tube,
        eyepiece,
        coarse_focus,
        fine_focus,
    )


def example() -> Canvas:
    """Compose two projections of the same named parts, then add 2D typography."""
    canvas = Canvas(310, 265)
    canvas.draw(Rectangle((0, 0), 310, 265), Style(stroke=None, fill=Color(0.97, 0.96, 0.93)))
    font = latin_font()

    def label(text: str, x: float, y: float, size: float = 10, color: Color = INK) -> None:
        canvas.draw(
            Text(text, font=font, position=(x, y), size=size), Style(stroke=None, fill=color)
        )

    label("FIELD NOTES     /     INSTRUMENT SERIES 01", 14, 249, 9, BLUE)
    label("The optical microscope", 14, 234, 28)
    label("A study in assemblies, light and precision", 15, 224, 11)
    canvas.draw(Line((14, 217), (296, 217)), Style(stroke=BLUE, line_width=0.4))
    parts = microscope_parts()
    for exploded, x, y in ((False, 65, 52), (True, 206, 44)):
        solids = tuple(solid for part in parts for solid in part.placed(exploded))
        projection = Scene3D(solids, CAMERA, LIGHT).project()
        canvas.draw(Drawing(projection, transform=Transform.translate(x, y)))
        label("02 / EXPLODED" if exploded else "01 / ASSEMBLED", x - 43, 19, 11, BLUE)
    # Annotation targets share the same camera and placement as the exploded scene.
    by_name = {part.name: part for part in parts}
    for part_name, caption, height, label_y in (
        ("Eyepiece", "Eyepiece", 13, 192),
        ("Body tube", "Body tube", 13, 165),
        ("Revolving nosepiece", "Nosepiece", 3, 141),
        ("Objective 1", "Objectives", 8, 120),
        ("Specimen slide", "Specimen slide", 1, 96),
        ("Condenser", "Condenser", 5, 71),
    ):
        part = by_name[part_name]
        target = part.origin + part.explosion + Vector3D(0, 0, height)
        point = CAMERA.project(target)
        start = (point.x + 206, point.y + 44)
        canvas.draw(Line(start, (263, label_y)), Style(stroke=BLUE, line_width=0.18))
        canvas.draw(Line((263, label_y), (267, label_y)), Style(stroke=BLUE, line_width=0.18))
        label(caption, 269, label_y - 1, 8)
    label("PARAMETRIC VECTOR STUDY", 14, 10, 8, BLUE)
    label("15 named parts  /  orthographic projection  /  SVG + TikZ", 130, 10, 8)
    return canvas


if __name__ == "__main__":
    export(example(), __file__, tikz_mode="pdf")
