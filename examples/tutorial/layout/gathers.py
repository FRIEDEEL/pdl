# tutorial-start
from pdl import Canvas, Circle, Color, Gather, Group, Rectangle, Style

body = Rectangle((10, 10), 16, 10).set_style(Style(fill=Color(0.6, 0.8, 1)))
port = Circle((29, 15), 2).set_style(Style(fill=Color(1, 0.7, 0.35)))
component = Group((body, port))
marker = Circle((45, 15), 4).set_style(Style(fill=Color(0.6, 0.9, 0.7)))
first = Gather(component, marker)
second = Gather(component)
combined = Gather(first, second)

canvas = Canvas(85, 65)
canvas.draw(component)
canvas.draw(marker)
combined.translate(10, 25)
second.rotate(20, about=(30, 40))
canvas.draw(component)
canvas.draw(marker)

# tutorial-end

if __name__ == "__main__":
    from pathlib import Path as FilePath

    output = FilePath(__file__).resolve().parents[2] / "output" / "tutorial" / "layout"
    output.mkdir(parents=True, exist_ok=True)
    canvas.save(output / "gathers.svg")
