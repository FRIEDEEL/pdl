"""All five Platonic solids, one camera and one parallel light.

Run: uv run python -m examples.spatial.platonic_solids
"""

from examples._shared import export, latin_font
from pdl import (
    Canvas,
    Color,
    DirectionalLight,
    Entity,
    OrthographicCamera,
    Scene3D,
    Style,
    Transform3D,
    Translation,
    Vector3D,
    regular_polyhedron,
    text,
)
from pdl.author.entity.factories import as_entity
from pdl.extensions.spacial.solids import PlatonicKind

# Edit these shared parameters to compare lighting and viewing directions.
CAMERA = OrthographicCamera(azimuth=30, elevation=22)
LIGHT = DirectionalLight(direction=Vector3D(-1, 1, -2), ambient=0.22)
BASE_COLOR = Color(0.38, 0.73, 0.91)
SOLIDS: tuple[tuple[PlatonicKind, str, int, int, int], ...] = (
    ("tetrahedron", "Tetrahedron", 4, 6, 4),
    ("cube", "Cube", 8, 12, 6),
    ("octahedron", "Octahedron", 6, 12, 8),
    ("dodecahedron", "Dodecahedron", 20, 30, 12),
    ("icosahedron", "Icosahedron", 12, 30, 20),
)


def example() -> Canvas:
    canvas = Canvas(250, 100)
    font = latin_font()
    ink = Style(stroke=None, fill=Color(0.12, 0.18, 0.25))
    muted = Style(stroke=None, fill=Color(0.38, 0.43, 0.48))
    scenes: list[Entity] = []
    labels: list[Entity] = []
    details: list[Entity] = []
    for i, (kind, name, vertices, edges, faces) in enumerate(SOLIDS):
        center = 26 + i * 49
        solid = regular_polyhedron(kind, radius=20, color=BASE_COLOR)
        solid = solid.transformed(Transform3D.rotate(12, Vector3D(0, 0, 1)))
        scene = Scene3D((solid,), camera=CAMERA, light=LIGHT).project()
        scenes.append(as_entity(scene, transform=Translation(center, 46)))
        labels.append(text(name, font=font, position=(center - 19, 17), size=11))
        details.append(
            text(
                f"V {vertices}   E {edges}   F {faces}",
                font=font,
                position=(center - 19, 10),
                size=8,
            )
        )
    title = text("The five Platonic solids", font=font, position=(7, 89), size=19)
    subtitle = text(
        "Orthographic view / equal circumradius / shared intrinsic color",
        font=font,
        position=(7, 80),
        size=10,
    )
    lighting = text(
        "Light travels along (-1, 1, -2); ambient = 0.22", font=font, position=(7, 73), size=9
    )

    canvas.draw(title, ink)
    canvas.draw(subtitle, muted)
    canvas.draw(lighting, muted)
    for scene in scenes:
        canvas.draw(scene)
    for label in labels:
        canvas.draw(label, ink)
    for detail in details:
        canvas.draw(detail, muted)
    return canvas


if __name__ == "__main__":
    export(example(), __file__, tikz_mode="pdf")
