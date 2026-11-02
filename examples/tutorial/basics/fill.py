from pathlib import Path

from pdl import Canvas, Color, Style, circle

circle_entity = circle((20, 20), radius=10)
blue = Color(0.15, 0.35, 0.75)
light_blue = Color(0.75, 0.85, 1.0)

canvas = Canvas(40, 40)
canvas.draw(circle_entity, Style(stroke=blue, fill=light_blue, line_width=0.5))

output = Path(__file__).resolve().parents[2] / "output" / "tutorial" / "basics"
output.mkdir(parents=True, exist_ok=True)
canvas.save(output / "fill.svg")
