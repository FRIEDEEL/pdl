from pathlib import Path

from pdl import Canvas, Circle, Color, Style

circle = Circle((20, 20), radius=10)
light_blue = Color(0.75, 0.85, 1.0)

canvas = Canvas(40, 40)
canvas.draw(circle, Style(stroke=None, fill=light_blue))

output = Path(__file__).resolve().parents[2] / "output" / "tutorial" / "basics"
output.mkdir(parents=True, exist_ok=True)
canvas.save(output / "fill_only.svg")
