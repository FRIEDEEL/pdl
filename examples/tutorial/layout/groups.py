# tutorial-start
from pdl import Canvas, Color, Group, Style, circle, rectangle

body = rectangle((-8, -5), 16, 10)
port = circle((11, 0), 2).set_style(Style(fill=Color(1, 0.7, 0.35), line_width=0.5))
component = Group(body, port, style=Style(fill=Color(0.6, 0.8, 1), line_width=0.5))
first = component.copy().translate(20, 20)
second = component.copy().rotate(45, origin=(0, 0)).translate(60, 20)
canvas = Canvas(85, 45)
canvas.draw(first)
canvas.draw(second)
# tutorial-end

if __name__ == "__main__":
    from pathlib import Path as FilePath

    output = FilePath(__file__).resolve().parents[2] / "output" / "tutorial" / "layout"
    output.mkdir(parents=True, exist_ok=True)
    canvas.save(output / "groups.svg")
