"""Shared identity changes another Gather's relative member placement."""

from pdl import Canvas, Circle, Color, Gather, Style, Text

INK = Style(stroke=None, fill=Color(0.12, 0.18, 0.25))
BLUE = Style(stroke=Color(0.15, 0.35, 0.6), fill=Color(0.4, 0.7, 1), line_width=0.4)
GHOST = Style(stroke=Color(0.65, 0.68, 0.72), fill=Color(0.85, 0.87, 0.9), opacity=0.35)

# tutorial-start
canvas = Canvas(110, 118)
for step, baseline in enumerate((72, 18)):
    a = Circle((18, baseline), 6).set_style(BLUE)
    b = Circle((44, baseline), 6).set_style(BLUE)
    c = Circle((70, baseline), 6).set_style(BLUE)
    g1 = Gather(a, b)
    g2 = Gather(b, c)  # The very same B, not a copy.

    for member in (a, b, c):
        canvas.draw(member, GHOST)

    g1.translate(0, 14)  # Both A and B move; g2's B-to-C relation changes.
    if step == 1:
        g2.translate(14, 0)  # Both B and C move; g1's A-to-B relation changes.

    for name, member in zip(("A", "B", "C"), (a, b, c), strict=True):
        label = Text(name, size=11).set_style(INK).move_to(member.anchor(), anchor="center")
        canvas.draw(member)
        canvas.draw(label)

    title = "1. g1: A + B move up" if step == 0 else "2. Then g2: B + C move right"
    canvas.draw(Text(title, position=(5, baseline + 33), size=13), INK)
# tutorial-end

if __name__ == "__main__":
    from pathlib import Path as FilePath

    output = FilePath(__file__).resolve().parents[2] / "output" / "tutorial" / "layout"
    output.mkdir(parents=True, exist_ok=True)
    canvas.save(output / "shared_gathers.svg")
    canvas.save(output / "shared_gathers.tex", backend="tikz")
