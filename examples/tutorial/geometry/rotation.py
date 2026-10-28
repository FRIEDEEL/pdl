# tutorial-start
from pdl import Canvas, Circle, Color, Rectangle, Style

box = Rectangle((15, 15), width=20, height=10)
ghost = Style(stroke=Color(0.65, 0.65, 0.65), line_width=0.3)
blue = Style(fill=Color(0.6, 0.8, 1), line_width=0.5)
pivot = Circle((25, 20), radius=0.7)

canvas = Canvas(50, 40)
canvas.draw(box, ghost)
box.rotate(30, center=(25, 20))
canvas.draw(box, blue)
canvas.draw(pivot, Style(stroke=None, fill=Color(0.85, 0.2, 0.15)))

# tutorial-end

if __name__ == "__main__":
    from pathlib import Path as FilePath

    output = FilePath(__file__).resolve().parents[2] / "output" / "tutorial" / "geometry"
    output.mkdir(parents=True, exist_ok=True)
    canvas.save(output / "rotation.svg")
