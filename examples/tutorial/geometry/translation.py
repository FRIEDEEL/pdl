# tutorial-start
from pdl import Canvas, Color, Rectangle, Style

box = Rectangle((10, 10), width=20, height=10)
ghost = Style(stroke=Color(0.65, 0.65, 0.65), line_width=0.3)
blue = Style(fill=Color(0.6, 0.8, 1), line_width=0.5)

canvas = Canvas(70, 40)
canvas.draw(box, ghost)
box.translate(25, 10)
canvas.draw(box, blue)

# tutorial-end

if __name__ == "__main__":
    from pathlib import Path as FilePath

    output = FilePath(__file__).resolve().parents[2] / "output" / "tutorial" / "geometry"
    output.mkdir(parents=True, exist_ok=True)
    canvas.save(output / "translation.svg")
