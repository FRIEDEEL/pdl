# tutorial-start
from pdl import Canvas, Circle, Color, Gather, Style

left = Circle((22, 20), 12).set_style(Style(stroke=None, fill=Color(0.1, 0.4, 0.8)))
right = Circle((36, 20), 12).set_style(Style(stroke=None, fill=Color(0.1, 0.4, 0.8)))
Gather(left, right).set_opacity(0.5)

canvas = Canvas(60, 40)
canvas.draw(left)
canvas.draw(right)

# tutorial-end

if __name__ == "__main__":
    from pathlib import Path as FilePath

    output = FilePath(__file__).resolve().parents[2] / "output" / "tutorial" / "paint"
    output.mkdir(parents=True, exist_ok=True)
    canvas.save(output / "opacity.svg")
