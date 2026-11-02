"""Reusable components, nested groups and affine instance placement."""

from examples._shared import BLUE, INK, LABEL, PALE, export, valve
from pdl import (
    Canvas,
    Circle,
    Group,
    Line,
    RendererConfig,
    Rotation,
    Scaling,
    Style,
    Text,
    Translation,
)
from pdl.author.entity.factories import as_entity


def example() -> Canvas:
    canvas = Canvas(160, 102, renderer=RendererConfig(fonts=("sans-serif",)))
    title = Text("Reusable components / local coordinates", size=16, position=(8, 92))
    body = valve()
    original = body.copy().apply_transform(Translation(25, 66))
    rotated = body.copy().apply_transform(Translation(70, 66) @ Rotation(90))
    scaled = body.copy().apply_transform(Translation(120, 66) @ Scaling(2, 1.4))
    captions = (
        Text("original", align="center", position=(25, 48)),
        Text("rotate 90 deg", align="center", position=(70, 48)),
        Text("scale (2, 1.4)", align="center", position=(120, 48)),
    )
    pipe = Line((-20, 0), (20, 0))
    vessel = Circle((15, 0), 6)
    assembly = Group(
        as_entity(pipe, INK),
        as_entity(body),
        as_entity(vessel, Style(stroke=BLUE, fill=PALE, line_width=0.45)),
    )
    first = assembly.copy().apply_transform(Translation(40, 24))
    second = assembly.copy().apply_transform(Translation(112, 23) @ Rotation(25) @ Scaling(0.8))
    note = Text(
        "Two instances share one definition; stroke stays 0.45 mm.", size=9, position=(8, 6)
    )
    canvas.draw(title, LABEL)
    for component in (original, rotated, scaled, first, second):
        canvas.draw(component)
    for caption in (*captions, note):
        canvas.draw(caption, LABEL)
    return canvas


if __name__ == "__main__":
    export(example(), __file__)
