# tutorial-start
from pdl import Canvas, Circle, Color, Connection, Entity, Node, Style, Text

left = Node(Text("Start"), position=(20, 20))
right = Node(Text("Finish"), position=left.anchor("east") + (35, 0))
link = Connection(left.anchor("east"), right.anchor("west"))

canvas = Canvas(90, 40)
canvas.draw(link)
canvas.draw(left)
canvas.draw(right)

# Optional guide dots mark the connection endpoints.
red = Style(stroke=None, fill=Color(0.85, 0.2, 0.15))
canvas.draw(Entity(Circle((0, 0), radius=0.7)).move_to(left.anchor("east")), red)
canvas.draw(Entity(Circle((0, 0), radius=0.7)).move_to(right.anchor("west")), red)

# tutorial-end

if __name__ == "__main__":
    from pathlib import Path as FilePath

    output = FilePath(__file__).resolve().parents[2] / "output" / "tutorial" / "layout"
    output.mkdir(parents=True, exist_ok=True)
    canvas.save(output / "anchors.svg")
