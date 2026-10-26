"""A small manually positioned vacuum topology with reusable valve symbols."""

from examples._shared import BLUE, LABEL, PALE, export, valve
from pdl import Canvas, Connection, Node, Style, TeX, Text, Transform


def example() -> Canvas:
    paint = Style(stroke=BLUE, fill=PALE, line_width=0.45)
    title = Text("Vacuum system / topology and scientific labels", size=16, position=(8, 131))
    chamber = Node(
        Text("Vacuum chamber\nSample stage", size=13),
        (100, 94),
        min_width=46,
        min_height=23,
        style=paint,
    )
    turbo = Node(Text("Turbo\npump"), (155, 39), shape="circle", style=paint)
    backing = Node(Text("Backing\npump"), (55, 39), shape="circle", style=paint)
    vent = Node(Text("Vent"), (28, 94), min_width=20, style=paint)
    gauge = Node(Text("Pressure\ngauge"), (166, 94), style=paint)
    main_pipe = Connection(
        chamber.anchor("south"), turbo.anchor("north"), via=((100, 64), (155, 64))
    )
    backing_pipe = Connection(turbo.anchor("west"), backing.anchor("east"))
    vent_pipe = Connection(vent.anchor("east"), chamber.anchor("west"), arrow_end=False)
    gauge_pipe = Connection(chamber.anchor("east"), gauge.anchor("west"), arrow_end=False)
    valve_symbol = valve()
    valves = (
        valve_symbol.transformed(Transform.translate(128, 64)),
        valve_symbol.transformed(Transform.translate(102, 39)),
        valve_symbol.transformed(Transform.translate(56, 94)),
    )
    pressure = TeX("$p < 10^{-6}\\,\\mathrm{mbar}$", (80, 115), size=13)
    labels = (
        Text("V1", align="center", size=10, position=(128, 75)),
        Text("V2", align="center", size=10, position=(102, 50)),
        Text("V3", align="center", size=10, position=(56, 106)),
        Text(
            "Manual placement / reusable components / baseline-aware labels",
            size=10,
            position=(8, 8),
        ),
    )
    canvas = Canvas(200, 143)
    canvas.draw(title, LABEL)
    for connection in (main_pipe, backing_pipe, vent_pipe, gauge_pipe):
        canvas.draw(connection)
    for node in (chamber, turbo, backing, vent, gauge):
        canvas.draw(node)
    for placed in valves:
        canvas.draw(placed)
    canvas.draw(pressure)
    for label in labels:
        canvas.draw(label, LABEL)
    return canvas


if __name__ == "__main__":
    export(example(), __file__)
