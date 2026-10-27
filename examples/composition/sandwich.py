"""The sandwich case: spatial groups, cross-layer Gather, and regrouping."""

from pdl import Canvas, Circle, Color, Entity, Gather, Group, Rectangle, Style, Text

INK = Color(0.12, 0.18, 0.25)
BLUE = Color(0.25, 0.55, 0.82)
TEAL = Color(0.2, 0.68, 0.63)
ORANGE = Color(1, 0.68, 0.25)
LABEL = Style(stroke=None, fill=INK)


def plate(x: float, y: float, width: float, color: Color, label: str) -> Group:
    """Keep the plate, its two bolts, and its label in one spatial unit."""
    body = Entity(
        Rectangle((x, y), width, 12),
        style=Style(stroke=INK, fill=color, line_width=0.35),
    )
    bolts = tuple(
        Entity(Circle((px, y + 6), 1.2), style=Style(stroke=None, fill=INK))
        for px in (x + 4, x + width - 4)
    )
    text = Entity(
        Text(label, size=11, position=(x + width / 2, y + 4.5), align="center"), style=LABEL
    )
    return Group((body, *bolts, text))


def example() -> Canvas:
    # tutorial-start
    canvas = Canvas(112, 214)
    bottom_layer, middle_layer, top_layer = (canvas.layers[i] for i in range(3))
    titles = ("1. Separate layers", "2. Gather: move both", "3. Group: one layer")
    notes = (
        "Base < middle < lid",
        "Base + lid move right; middle stays",
        "Base now covers the middle's lower edge",
    )
    for case, y in enumerate((154, 85, 16)):
        base = plate(8, y + 6, 68, TEAL, "BASE")
        middle = plate(25, y + 15, 68, ORANGE, "MIDDLE")
        lid = plate(16, y + 24, 68, BLUE, "LID")
        base.set_layer(bottom_layer)
        middle.set_layer(middle_layer)
        lid.set_layer(top_layer)

        if case >= 1:
            shell = Gather(base, lid)
            shell.translate(10, 0)

        if case == 2:
            # A real Group cannot straddle layers: it rises to the highest one.
            combined = Group((base, lid))
            canvas.draw(combined)
        else:
            # Deliberately submit the lid first: Layer still controls coverage.
            canvas.draw(lid)
            canvas.draw(base)
        canvas.draw(middle)
        canvas.draw(Text(titles[case], position=(6, y + 47), size=15), LABEL)
        canvas.draw(Text(notes[case], position=(6, y - 3), size=10), LABEL)
    return canvas
    # tutorial-end


if __name__ == "__main__":
    from examples._shared import export

    export(example(), __file__)
