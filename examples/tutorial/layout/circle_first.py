# tutorial-start
from pdl import Canvas, Circle, Color, Rectangle, Style

circle = Circle((28, 20), radius=12)
rectangle = Rectangle((28, 10), width=28, height=20)
blue = Style(fill=Color(0.6, 0.8, 1), line_width=0.5)
orange = Style(fill=Color(1, 0.7, 0.35), line_width=0.5)

canvas = Canvas(70, 40)
canvas.draw(circle, blue)
canvas.draw(rectangle, orange)

# tutorial-end

if __name__ == "__main__":
    from pathlib import Path as FilePath

    output = FilePath(__file__).resolve().parents[2] / "output" / "tutorial" / "layout"
    output.mkdir(parents=True, exist_ok=True)
    canvas.save(output / "circle_first.svg")
