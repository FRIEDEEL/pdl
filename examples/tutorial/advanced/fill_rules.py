# tutorial-start
from pdl import Canvas, Circle, Color, Drawing, Path, Style, Transform

rings = Path().extend(Circle((15, 15), radius=10)).extend(Circle((15, 15), radius=5))
blue = Color(0.6, 0.8, 1)

canvas = Canvas(65, 30)
canvas.draw(rings, Style(fill=blue, line_width=0.4, fill_rule="nonzero"))
canvas.draw(
    Drawing(rings, transform=Transform.translate(35, 0)),
    Style(fill=blue, line_width=0.4, fill_rule="evenodd"),
)

# tutorial-end

if __name__ == "__main__":
    from pathlib import Path as FilePath

    output = FilePath(__file__).resolve().parents[2] / "output" / "tutorial" / "advanced"
    output.mkdir(parents=True, exist_ok=True)
    canvas.save(output / "fill_rules.svg")
