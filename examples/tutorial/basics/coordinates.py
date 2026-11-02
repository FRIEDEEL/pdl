from pathlib import Path

from pdl import Canvas, Color, Style, circle, line, text

circle_entity = circle((20, 15), radius=5)

canvas = Canvas(45, 35)
canvas.draw(circle_entity)

# Optional guides: the actual origin is the lower-left corner of the canvas.
guide = Style(stroke=Color(0.65, 0.65, 0.65), line_width=0.2)
canvas.draw(line((0, 0), (40, 0)), guide)
canvas.draw(line((0, 0), (0, 30)), guide)
canvas.draw(line((20, 0), (20, 15)), guide)
canvas.draw(line((0, 15), (20, 15)), guide)
canvas.draw(text("0", position=(1, 1), size=8))
canvas.draw(text("x", position=(41, 1), size=8))
canvas.draw(text("y", position=(1, 30), size=8))
canvas.draw(text("20", position=(21, 1), size=8))
canvas.draw(text("15", position=(1, 16), size=8))
canvas.draw(text("(20, 15)", position=(26, 15), size=8))

output = Path(__file__).resolve().parents[2] / "output" / "tutorial" / "basics"
output.mkdir(parents=True, exist_ok=True)
canvas.save(output / "coordinates.svg")
