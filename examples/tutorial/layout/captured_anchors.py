# tutorial-start
from pdl import Canvas, Circle, Color, Connection, Entity, Rectangle, Style

box = Entity(Rectangle((-10, -5), width=20, height=10)).move_to((20, 20))
old_attachment = Entity(Circle((0, 0), radius=3)).move_to(box.anchor("east") + (10, 0))
box.translate(0, 20)
new_attachment = Entity(Circle((0, 0), radius=3)).move_to(box.anchor("east") + (10, 0))
link = Connection(box.anchor("east"), new_attachment.anchor("west"))

canvas = Canvas(65, 55)
canvas.draw(link)
canvas.draw(box, Style(fill=Color(0.6, 0.8, 1), line_width=0.5))
canvas.draw(old_attachment, Style(fill=Color(1, 0.7, 0.35), line_width=0.5))
canvas.draw(new_attachment, Style(fill=Color(0.4, 0.75, 0.55), line_width=0.5))

# tutorial-end

if __name__ == "__main__":
    from pathlib import Path as FilePath

    output = FilePath(__file__).resolve().parents[2] / "output" / "tutorial" / "layout"
    output.mkdir(parents=True, exist_ok=True)
    canvas.save(output / "captured_anchors.svg")
