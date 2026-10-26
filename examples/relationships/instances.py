"""Local relationships travel with groups; external links address instances."""

from examples._shared import BLUE, LABEL, PALE, export
from pdl import Canvas, Connection, Drawing, Group, Node, Style, Text, Transform


def example() -> Canvas:
    paint = Style(stroke=BLUE, fill=PALE, line_width=0.45)
    inlet = Node(Text("In"), position=(-18, 0), style=paint)
    outlet = Node(Text("Out"), position=(18, 0), style=paint)
    local_pipe = Connection(inlet.anchor("east"), outlet.anchor("west"))
    assembly = Group((Drawing(local_pipe), Drawing(inlet), Drawing(outlet)))
    first = assembly.transformed(Transform.translate(42, 90))
    second = assembly.transformed(Transform.translate(156, 90) @ Transform.rotate(15))
    first_outlet = first.child(2)
    second_inlet = second.child(1)
    between_groups = Connection(first_outlet.anchor("east"), second_inlet.anchor("west"))

    pump = Node(Text("P"), shape="circle", min_width=15, style=paint)
    left_pump = Drawing(pump, transform=Transform.translate(42, 35))
    right_pump = Drawing(pump, transform=Transform.translate(156, 35) @ Transform.rotate(30))
    between_pumps = Connection(left_pump.anchor("east"), right_pump.anchor("west"))
    title = Text("Reuse definitions. Connect placed instances.", position=(8, 124), size=16)
    captions = (
        Text("One group, two placements; internal links move together.", position=(8, 66), size=10),
        Text("One node, two placements; anchors follow rotation.", position=(8, 8), size=10),
    )

    canvas = Canvas(210, 137)
    canvas.draw(between_groups)
    canvas.draw(between_pumps)
    for instance in (first, second, left_pump, right_pump):
        canvas.draw(instance)
    for text in (title, *captions):
        canvas.draw(text, LABEL)
    return canvas


if __name__ == "__main__":
    export(example(), __file__)
