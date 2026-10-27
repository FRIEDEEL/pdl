"""Capture, transform and reattach a square, triangle and circles.

Run: uv run python -m examples.coordinates.relationships
"""

from typing import Literal

from examples._shared import export, output_base
from pdl import (
    Canvas,
    Circle,
    Color,
    Connection,
    CoordinateSystem,
    Drawing,
    Entity,
    Group,
    Line,
    Node,
    Polygon,
    Rectangle,
    Style,
    Text,
    Transform,
)

BLUE = Style(fill=Color(0.72, 0.85, 1), line_width=0.5, line_join="round")
ORANGE = Style(fill=Color(1, 0.76, 0.43), line_width=0.5, line_join="round")
GREEN = Style(fill=Color(0.65, 0.87, 0.72), line_width=0.5, line_join="round")
GHOST = Style(stroke=Color(0.65, 0.68, 0.73), line_width=0.3)


def example(mode: Literal["fit", "auto_size", "clip"] = "fit") -> Canvas:
    # All source coordinates are integers. The shared frame can be remapped
    # per canvas without changing any shape or relationship description.
    world = CoordinateSystem(name="example")
    row = world.child(Transform.translate(18, 70), name="original-row")

    square = Entity(Rectangle((-8, -8), 16, 16), style=BLUE, space=row)
    triangle = Entity(Polygon(((-7, -6), (7, -6), (0, 8))), style=ORANGE)
    triangle.move_to(square.space.point(30, 0))
    circle = Entity(Circle((0, 0), 7), style=GREEN)
    circle.move_to(triangle.anchor("east") + (18, 0))

    # Capture the original relation before moving the source square.
    fixed_marker = Entity(Circle((0, 0), 2), style=ORANGE)
    fixed_marker.move_to(square.anchor("north") + (0, 6))
    original_square = square.snapshot()
    original_east = square.anchor("east")

    # New state: rotate and translate only the square. Existing dependents
    # keep their captured source state. A new attachment uses the new state.
    square.rotate(25, center=(18, 70)).translate(0, -34)
    new_attachment = Entity(Circle((0, 0), 3), style=GREEN)
    new_attachment.move_to(square.anchor("east") + (8, 0))

    # Reuse the original three-part assembly under a reflected, rotated frame.
    assembly = Group(
        (Drawing(original_square), Drawing(triangle.snapshot()), Drawing(circle.snapshot()))
    )
    reflected = Drawing(
        assembly,
        transform=Transform.translate(205, 0) @ Transform.reflect(90),
    )
    turned = Drawing(
        assembly,
        transform=Transform.translate(95, -65) @ Transform.rotate(12),
    )

    # Both labels need font measurement. Their relative placement remains
    # authoring-only and is evaluated automatically by the canvas.
    label = Entity(Node(Text("Captured state")), space=world)
    label.move_to((45, -12))
    next_label = Entity(Node(Text("New attachment")), space=world)
    next_label.move_to(label.anchor("east") + (28, 0))

    old_link = Connection(original_east, triangle.anchor("west"))
    new_link = Connection(square.anchor("east"), new_attachment.anchor("west"))
    baseline = Line((4, 53), (190, 53))

    canvas = Canvas(210, 110, mode=mode, padding=6)
    canvas.map(world, Transform.translate(3, 2))
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
