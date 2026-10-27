from pathlib import Path

from pdl import Canvas, Circle, Color, Line, Style, Text

circle = Circle((20, 15), radius=5)

canvas = Canvas(45, 35)
canvas.draw(circle)

# Optional guides: the actual origin is the lower-left corner of the canvas.
guide = Style(stroke=Color(0.65, 0.65, 0.65), line_width=0.2)
canvas.draw(Line((0, 0), (40, 0)), guide)
canvas.draw(Line((0, 0), (0, 30)), guide)
canvas.draw(Line((20, 0), (20, 15)), guide)
canvas.draw(Line((0, 15), (20, 15)), guide)
canvas.draw(Text("0", position=(1, 1), size=8))
canvas.draw(Text("x", position=(41, 1), size=8))
canvas.draw(Text("y", position=(1, 30), size=8))
canvas.draw(Text("20", position=(21, 1), size=8))
canvas.draw(Text("15", position=(1, 16), size=8))
canvas.draw(Text("(20, 15)", position=(26, 15), size=8))

output = Path(__file__).resolve().parents[2] / "output" / "tutorial" / "basics"
output.mkdir(parents=True, exist_ok=True)
canvas.save(output / "coordinates.svg")
