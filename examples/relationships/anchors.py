"""Define relationships first; inspect the first render, then try other fonts."""

from pathlib import Path

from examples._shared import BLUE, LABEL, PALE, export, output_base
from pdl import Canvas, Connection, Node, RendererConfig, Style, Text


def example() -> Canvas:
    paint = Style(stroke=BLUE, fill=PALE, line_width=0.45)
    source = Node(Text("Source"), position=(28, 62), style=paint)
    process = Node(Text("Process data"), position=source.anchor("east") + (45, 0), style=paint)
    result = Node(Text("Result"), position=process.anchor("east") + (45, 0), style=paint)
    forward = Connection(source.anchor("east"), process.anchor("west"))
    output = Connection(process.anchor("east"), result.anchor("west"))
    feedback = Connection(
        result.anchor("south"),
        source.anchor("south"),
        via=(result.anchor("south") + (0, -25), source.anchor("south") + (0, -25)),
    )
    title = Text("Define objects and relationships. Then render.", position=(8, 91), size=16)
    route_label = Text("Feedback / via points also refer to anchors", position=(35, 27), size=10)
    note = Text(
        "Try another font on this same canvas; the anchors follow.", position=(8, 8), size=10
    )

    canvas = Canvas(210, 103)
    for connection in (forward, output, feedback):
        canvas.draw(connection)
    for node in (result, process, source):
        canvas.draw(node)
    for text in (title, route_label, note):
        canvas.draw(text, LABEL)
    return canvas


def export_variants(canvas: Canvas) -> tuple[Path, ...]:
    """Adjust only render settings after the unconfigured first export."""
    paths: list[Path] = []
    for family in ("sans-serif", "serif"):
        config = RendererConfig(fonts=(family,))
        base = output_base(__file__).with_name(f"anchors-{family}")
        base.with_suffix(".svg").write_text(canvas.render("svg", renderer=config), encoding="utf-8")
        base.with_suffix(".tex").write_text(
            canvas.render("tikz", renderer=config), encoding="utf-8"
        )
        paths.append(base)
    return tuple(paths)


if __name__ == "__main__":
    canvas = example()
    export(canvas, __file__)
    export_variants(canvas)
