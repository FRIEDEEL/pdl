# tutorial-start
from pdl import Canvas, Circle, Color, Entity, Group, Rectangle, Style

body = Entity(Rectangle((10, 12), 18, 12), style=Style(fill=Color(0.6, 0.8, 1)))
port = Entity(Circle((31, 18), 3), style=Style(fill=Color(1, 0.7, 0.35)))
component = Group((body, port))

canvas = Canvas(90, 45)
canvas.draw(component)
component.rotate(25, center=(22, 18)).translate(45, 0)
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
