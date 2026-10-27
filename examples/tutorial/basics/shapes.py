from pathlib import Path

from pdl import Canvas, Circle, Polygon, Rectangle

triangle = Polygon(((10, 10), (30, 10), (20, 30)))
rectangle = Rectangle((40, 10), width=25, height=20)
circle = Circle((85, 20), radius=10)

canvas = Canvas(105, 40)
canvas.draw(triangle)
canvas.draw(rectangle)
canvas.draw(circle)

output = Path(__file__).resolve().parents[2] / "output" / "tutorial" / "basics"
output.mkdir(parents=True, exist_ok=True)
canvas.save(output / "shapes.svg")
