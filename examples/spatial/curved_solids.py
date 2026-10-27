"""Smooth vector gradients for cylinders and spheres, without surface facets.

Run: uv run python -m examples.spatial.curved_solids
"""

from examples._shared import export, latin_font, output_base
from pdl import (
    Canvas,
    Color,
    Cylinder,
    DirectionalLight,
    Drawing,
    OrthographicCamera,
    Point3D,
    Scene3D,
    Sphere,
    Style,
    Text,
    Transform,
    Vector3D,
)

CAMERA = OrthographicCamera(30, 25)
COLOR = Color(0.32, 0.7, 0.91)
INK = Style(stroke=None, fill=Color(0.12, 0.18, 0.25))


def example() -> Canvas:
    viewer, right, up = CAMERA.toward_viewer, CAMERA.right, CAMERA.up
    lights = (
        ("Upper left", DirectionalLight(viewer * -1 + right + up * -1, ambient=0.2)),
        ("Upper right", DirectionalLight(viewer * -1 + right * -1 + up * -1, ambient=0.2)),
        ("Backlight", DirectionalLight(viewer, ambient=0.2)),
        ("No lighting", None),
    )
    sphere = Sphere(radius=16, color=COLOR)
    cylinder = Cylinder(base=Point3D(0, 0, -16), radius=12, height=32, color=COLOR)
    panels: list[Drawing] = []
    labels: list[Text] = []
    font = latin_font()
    for i, (label, light) in enumerate(lights):
        x = 35 + i * 52
        panels.append(
            Drawing(Scene3D((sphere,), CAMERA, light), transform=Transform.translate(x, 90))
        )
        panels.append(
            Drawing(Scene3D((cylinder,), CAMERA, light), transform=Transform.translate(x, 38))
        )
        labels.append(Text(label, font=font, position=(x - 17, 115), size=11))
    title = Text("Smooth curved solids", font=font, position=(8, 140), size=20)
    subtitle = Text(
        "Sphere: radial approximation / Cylinder: Lambert-sampled linear gradient",
        font=font,
        position=(8, 130),
        size=10,
    )
    note = Text(
        "One intrinsic color; ambient = 0.20. Vector fills, no surface facets.",
        font=font,
        position=(8, 8),
        size=10,
    )
    canvas = Canvas(225, 150)
    canvas.draw(title, INK)
    canvas.draw(subtitle, INK)
    for panel in panels:
        canvas.draw(panel)
    for label in labels:
        canvas.draw(label, INK)
    canvas.draw(note, INK)
    return canvas


def views() -> Canvas:
    cylinder = Cylinder(base=Point3D(0, 0, -16), radius=12, height=32, color=COLOR)
    cameras = (
        ("Along axis", OrthographicCamera(0, 90)),
        ("Side view", OrthographicCamera(0, 0)),
        ("From below", OrthographicCamera(30, -35)),
        ("Oblique axis", OrthographicCamera(30, 30)),
    )
    tilted = Cylinder(
        base=Point3D(-10, 0, -10), radius=10, height=32, axis=Vector3D(1, 1, 1), color=COLOR
    )
    canvas = Canvas(225, 85)
    font = latin_font()
    panels: list[Drawing] = []
    labels: list[Text] = []
    for i, (label, camera) in enumerate(cameras):
        obj = tilted if i == 3 else cylinder
        panels.append(
            Drawing(Scene3D((obj,), camera), transform=Transform.translate(32 + i * 53, 39))
        )
        labels.append(Text(label, font=font, position=(15 + i * 53, 10), size=10))
    title = Text("Cylinder camera and axis checks", font=font, position=(8, 72), size=16)
    canvas.draw(title, INK)
    for panel in panels:
        canvas.draw(panel)
    for label in labels:
        canvas.draw(label, INK)
    return canvas


if __name__ == "__main__":
    export(example(), __file__, tikz_mode="pdf")
    base = output_base(__file__).with_name("curved_solids-views")
    canvas = views()
    canvas.save(base.with_suffix(".svg"))
    canvas.save(base.with_suffix(".tex"), backend="tikz", tikz_mode="pdf")
