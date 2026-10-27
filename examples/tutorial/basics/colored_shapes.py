from pathlib import Path

from pdl import Canvas, Circle, Color, Polygon, Rectangle, Style

triangle = Polygon(((10, 10), (30, 10), (20, 30)))
rectangle = Rectangle((40, 10), width=25, height=20)
circle = Circle((85, 20), radius=10)

blue = Style(stroke=Color(0.15, 0.35, 0.75), line_width=0.5)
orange = Style(fill=Color(1.0, 0.75, 0.4), line_width=0.5)
green = Style(stroke=None, fill=Color(0.4, 0.75, 0.55))

canvas = Canvas(105, 40)
canvas.draw(triangle, blue)
canvas.draw(rectangle, orange)
canvas.draw(circle, green)

output = Path(__file__).resolve().parents[2] / "output" / "tutorial" / "basics"
output.mkdir(parents=True, exist_ok=True)
canvas.save(output / "colored_shapes.svg")
