# tutorial-start
from pdl import Canvas, Circle, Color, Group, Rectangle, Style

body = Rectangle((10, 12), 18, 12).set_style(Style(fill=Color(0.6, 0.8, 1)))
port = Circle((31, 18), 3).set_style(Style(fill=Color(1, 0.7, 0.35)))
component = Group(body, port)

canvas = Canvas(90, 45)
canvas.draw(component)
component.rotate(25, origin=(22, 18)).translate(45, 0)
canvas.draw(component)
component.dismiss()
port.translate(0, 10)
canvas.draw(port)

# tutorial-end

if __name__ == "__main__":
    from pathlib import Path as FilePath

    output = FilePath(__file__).resolve().parents[2] / "output" / "tutorial" / "layout"
    output.mkdir(parents=True, exist_ok=True)
    canvas.save(output / "editable_groups.svg")
