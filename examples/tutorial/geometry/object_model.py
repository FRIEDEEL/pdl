"""Compare rectangle construction and capture two states of one drawing object."""

from pathlib import Path

# construction-start
from pdl import Canvas, Color, Entity, Style, rectangle, text
from pdl.author.geometry import Rectangle

# The factory creates a geometric description and wraps it in an Entity.
factory_rectangle = rectangle((40, 10), width=25, height=20)

# Construct the same kind of drawing object directly from its geometry.
geometry = Rectangle((40, 10), width=25, height=20)
explicit_rectangle = Entity(geometry)
# construction-end

# style-start
orange = Style(fill=Color(1.0, 0.75, 0.4), line_width=0.5)

styled_factory_rectangle = rectangle((40, 10), width=25, height=20, style=orange)

geometry = Rectangle((40, 10), width=25, height=20)
editable = Entity(geometry, style=orange)
# style-end

# capture-start
canvas = Canvas(100, 55)
canvas.draw(editable)  # Capture the current rectangle and its orange paint.

# Edit the source geometry, move the Entity, and replace its immutable Style.
geometry.width = 15
editable.translate(30, 15)
editable.set_style(Style(fill=Color(0.4, 0.6, 0.9), line_width=0.5))

canvas.draw(editable)  # Add a second impression; the first one stays unchanged.
# capture-end

canvas.draw(text("first draw", position=(52.5, 5), size=9, align="center"))
canvas.draw(text("second draw", position=(77.5, 20), size=9, align="center"))

output = Path(__file__).resolve().parents[2] / "output" / "tutorial" / "geometry"
output.mkdir(parents=True, exist_ok=True)
canvas.save(output / "object_model.svg")
