# tutorial-start
from pdl import Canvas, Circle, Color, Rectangle, ReferencePoint, Style

pivot = ReferencePoint((15, 15))
box = Rectangle((15, 15), 20, 10)
canvas = Canvas(55, 45)
canvas.draw(box, Style(stroke=Color(0.7, 0.7, 0.7), line_width=0.3))
box.rotate(30, about=pivot.position)
canvas.draw(box, Style(fill=Color(0.6, 0.8, 1), line_width=0.4))
canvas.draw(pivot)  # Reference objects produce no paint.
canvas.draw(Circle(pivot.position, 0.6), Style(stroke=None, fill=Color(0.8, 0.2, 0.2)))
# tutorial-end

if __name__ == "__main__":
    from pathlib import Path as FilePath

    output = FilePath(__file__).resolve().parents[2] / "output" / "tutorial" / "layout"
    output.mkdir(parents=True, exist_ok=True)
    canvas.save(output / "reference_points.svg")
