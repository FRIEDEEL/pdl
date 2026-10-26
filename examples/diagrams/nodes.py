"""Content-sized nodes with explicit anchors, routes and arrowheads."""

from examples._shared import BLUE, LABEL, PALE, export
from pdl import Canvas, Connection, Node, RendererConfig, Style, TeX, Text
from pdl.components.debug import debug_overlay

SHOW_DEBUG = False


def example() -> Canvas:
    canvas = Canvas(180, 125, renderer=RendererConfig(fonts=("sans-serif",)))
    paint = Style(stroke=BLUE, fill=PALE, line_width=0.45)
    title = Text("Nodes / content sizing and explicit connections", size=16, position=(8, 112))
    source = Node(Text("Source"), (30, 85), style=paint)
    process = Node(
        Text("A longer process label\nwith a second line"), (112, 85), padding=(4, 3), style=paint
    )
    sensor = Node(Text("Sensor"), (30, 35), shape="circle", style=paint)
    result = Node(
        TeX("$\\frac{x_i}{y^2}+\\alpha$", size=15), (112, 35), padding=(5, 3), style=paint
    )
    forward = Connection(canvas.anchor(source, "east"), canvas.anchor(process, "west"))
    down = Connection(canvas.anchor(process, "south"), canvas.anchor(result, "north"))
    feedback = Connection(
        canvas.anchor(result, "west"), canvas.anchor(sensor, "east"), arrow_start=True
    )
    measured = Connection(
        canvas.anchor(sensor, "north"), canvas.anchor(source, "south"), arrow_end=False
    )
    note = Text(
        "Positions and routes are explicit; no automatic layout or live references.",
        size=9,
        position=(8, 6),
    )
    canvas.draw(title, LABEL)
    for connection in (forward, down, feedback, measured):
        canvas.draw(connection)
    with canvas.typography():
        for node in (source, process, sensor, result):
            canvas.draw(node)
            if SHOW_DEBUG:
                canvas.draw(debug_overlay(node))
    canvas.draw(note, LABEL)
    return canvas


if __name__ == "__main__":
    export(example(), __file__)
