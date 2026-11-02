from pathlib import Path

from pdl import Canvas, Color, Style, circle, polygon, rectangle

triangle = polygon(((10, 10), (30, 10), (20, 30)))
rectangle_entity = rectangle((40, 10), width=25, height=20)
circle_entity = circle((85, 20), radius=10)

blue = Style(stroke=Color(0.15, 0.35, 0.75), line_width=0.5)
orange = Style(fill=Color(1.0, 0.75, 0.4), line_width=0.5)
green = Style(stroke=None, fill=Color(0.4, 0.75, 0.55))

canvas = Canvas(105, 40)
canvas.draw(triangle, blue)
canvas.draw(rectangle_entity, orange)
canvas.draw(circle_entity, green)

output = Path(__file__).resolve().parents[2] / "output" / "tutorial" / "basics"
output.mkdir(parents=True, exist_ok=True)
canvas.save(output / "colored_shapes.svg")
