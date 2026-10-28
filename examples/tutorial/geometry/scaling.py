# tutorial-start
from pdl import Canvas, Circle, Color, Style

circle = Circle((25, 20), radius=8)
ghost = Style(stroke=Color(0.65, 0.65, 0.65), line_width=0.3)
blue = Style(stroke=Color(0.15, 0.35, 0.75), line_width=0.5)

canvas = Canvas(50, 40)
canvas.draw(circle, ghost)
circle.scale(2, 0.75, about=(25, 20))
canvas.draw(circle, blue)

# tutorial-end

if __name__ == "__main__":
    from pathlib import Path as FilePath

    output = FilePath(__file__).resolve().parents[2] / "output" / "tutorial" / "geometry"
    output.mkdir(parents=True, exist_ok=True)
    canvas.save(output / "scaling.svg")
