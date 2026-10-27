from pathlib import Path

from pdl import Canvas, Circle, Color, Style

circle = Circle((20, 20), radius=10)
blue = Color(0.15, 0.35, 0.75)

canvas = Canvas(40, 40)
canvas.draw(circle, Style(stroke=blue, line_width=0.5))

output = Path(__file__).resolve().parents[2] / "output" / "tutorial" / "basics"
output.mkdir(parents=True, exist_ok=True)
canvas.save(output / "stroke.svg")
