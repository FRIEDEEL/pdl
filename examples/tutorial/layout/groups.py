# tutorial-start
from pdl import Canvas, Circle, Color, Drawing, Group, Rectangle, Style, Transform

body = Rectangle((-8, -5), width=16, height=10)
port = Circle((11, 0), radius=2)
component = Group(
    (
        Drawing(body, Style(fill=Color(0.6, 0.8, 1), line_width=0.5)),
        Drawing(port, Style(fill=Color(1, 0.7, 0.35), line_width=0.5)),
    )
)
first = Drawing(component, transform=Transform.translate(20, 20))
second = Drawing(component, transform=Transform.translate(60, 20) @ Transform.rotate(45))

canvas = Canvas(85, 45)
canvas.draw(first)
canvas.draw(second)

# tutorial-end

if __name__ == "__main__":
    from pathlib import Path as FilePath

    output = FilePath(__file__).resolve().parents[2] / "output" / "tutorial" / "layout"
    output.mkdir(parents=True, exist_ok=True)
    canvas.save(output / "groups.svg")
