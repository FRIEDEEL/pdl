"""Local relationships travel with groups; external links address instances."""

from examples._shared import BLUE, LABEL, PALE, export
from pdl import Canvas, Group, Style, text
from pdl.author.entity.factories import as_entity
from pdl.author.transform import Rotation, Translation
from pdl.extensions.diagram import Connection, Node


def example() -> Canvas:
    paint = Style(stroke=BLUE, fill=PALE, line_width=0.45)
    inlet = Node(text("In"), position=(-18, 0), style=paint)
    outlet = Node(text("Out"), position=(18, 0), style=paint)
    local_pipe = Connection(inlet.anchor("east"), outlet.anchor("west"))
    assembly = Group(as_entity(local_pipe), as_entity(inlet), as_entity(outlet))
    first = assembly.copy().apply_transform(Translation(42, 90))
    second = assembly.copy().apply_transform(Translation(156, 90) @ Rotation(15))
    first_outlet = first.members[2]
    second_inlet = second.members[1]
    between_groups = Connection(first_outlet.anchor("east"), second_inlet.anchor("west"))

    pump = Node(text("P"), shape="circle", min_width=15, style=paint)
    left_pump = as_entity(pump, transform=Translation(42, 35))
    right_pump = as_entity(pump, transform=Translation(156, 35) @ Rotation(30))
    between_pumps = Connection(left_pump.anchor("east"), right_pump.anchor("west"))
    title = text("Reuse definitions. Connect placed instances.", position=(8, 124), size=16)
    captions = (
        text("One group, two placements; internal links move together.", position=(8, 66), size=10),
        text("One node, two placements; anchors follow rotation.", position=(8, 8), size=10),
    )

    canvas = Canvas(210, 137)
    canvas.draw(between_groups)
    canvas.draw(between_pumps)
    for instance in (first, second, left_pump, right_pump):
        canvas.draw(instance)
    for text_entity in (title, *captions):
        canvas.draw(text_entity, LABEL)
    return canvas


if __name__ == "__main__":
    export(example(), __file__)
