"""Capture, transform and reattach a square, triangle and circles.

Run: uv run python -m examples.coordinates.relationships
"""

from typing import Literal

from examples._shared import export, output_base
from pdl import (
    WORLD,
    Canvas,
    Circle,
    Color,
    Connection,
    CoordinateSystem,
    Group,
    Line,
    Node,
    Polygon,
    Rectangle,
    Reflection,
    Rotation,
    Style,
    Text,
    Translation,
)
from pdl.author.entity.factories import as_entity

BLUE = Style(fill=Color(0.72, 0.85, 1), line_width=0.5, line_join="round")
ORANGE = Style(fill=Color(1, 0.76, 0.43), line_width=0.5, line_join="round")
GREEN = Style(fill=Color(0.65, 0.87, 0.72), line_width=0.5, line_join="round")
GHOST = Style(stroke=Color(0.65, 0.68, 0.73), line_width=0.3)


def example(mode: Literal["fit", "auto_size", "clip"] = "fit") -> Canvas:
    # Explicit Frame conversions are evaluated immediately into world points.
    # The Canvas can subsequently map the whole world into page coordinates.
    world = CoordinateSystem(name="example")
    row = world.child(Translation(18, 70), name="original-row")

    square = Rectangle((-8, -8), 16, 16).set_style(BLUE).apply_transform(row.matrix)
    triangle = Polygon(((-7, -6), (7, -6), (0, 8))).set_style(ORANGE)
    triangle.move_to(row.point((30, 0)), anchor="center")
    circle = Circle((0, 0), 7).set_style(GREEN)
    circle.move_to(triangle.anchor("east") + (18, 0))

    # Capture the original relation before moving the source square.
    fixed_marker = Circle((0, 0), 2).set_style(ORANGE)
    fixed_marker.move_to(square.anchor("north") + (0, 6))
    original_square = square.copy()
    original_east = square.anchor("east")

    # New state: rotate and translate only the square. Existing dependents
    # keep their captured source state. A new attachment uses the new state.
    square.rotate(25, origin=(18, 70)).translate(0, -34)
    new_attachment = Circle((0, 0), 3).set_style(GREEN)
    new_attachment.move_to(square.anchor("east") + (8, 0))

    # Reuse the original three-part assembly under a reflected, rotated frame.
    assembly = Group(
        as_entity(original_square), as_entity(triangle.copy()), as_entity(circle.copy())
    )
    reflected = as_entity(assembly, transform=Translation(205, 0) @ Reflection(90))
    turned = as_entity(assembly, transform=Translation(95, -65) @ Rotation(12))

    # Both labels need font measurement. Their relative placement remains
    # authoring-only and is evaluated automatically by the canvas.
    label = Node(Text("Captured state")).apply_transform(world.matrix)
    label.move_to((45, -12))
    next_label = Node(Text("New attachment")).apply_transform(world.matrix)
    next_label.move_to(label.anchor("east") + (28, 0))

    old_link = Connection(original_east, triangle.anchor("west"))
    new_link = Connection(square.anchor("east"), new_attachment.anchor("west"))
    baseline = Line((4, 53), (190, 53))

    canvas = Canvas(210, 110, mode=mode, padding=6)
    canvas.map(WORLD, Translation(3, 2))
    canvas.draw(baseline, GHOST)
    canvas.draw(old_link)
    canvas.draw(new_link)
    canvas.draw(original_square, GHOST)
    canvas.draw(fixed_marker)
    canvas.draw(triangle)
    canvas.draw(circle)
    canvas.draw(square)
    canvas.draw(new_attachment)
    canvas.draw(reflected)
    canvas.draw(turned)
    canvas.draw(label)
    canvas.draw(next_label)
    return canvas


def main() -> None:
    export(example(), __file__)
    base = output_base(__file__)
    for mode in ("auto_size", "clip"):
        canvas = example(mode)
        canvas.save(base.with_name(f"{base.name}-{mode}").with_suffix(".svg"))
        canvas.save(base.with_name(f"{base.name}-{mode}").with_suffix(".tex"), backend="tikz")


if __name__ == "__main__":
    main()
