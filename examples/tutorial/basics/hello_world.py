from pathlib import Path

from pdl import Canvas, text
from pdl.extensions.diagram import Node

# Create a text label and place it inside a rectangular node.
label = text("Hello world")
hello = Node(label, position=(30, 15))

# Create a drawing area 60 mm wide and 30 mm high.
canvas = Canvas(60, 30)
# Submit the node; creating it alone does not add it to the drawing.
canvas.draw(hello)

output = Path(__file__).resolve().parents[2] / "output" / "tutorial" / "basics"
output.mkdir(parents=True, exist_ok=True)
# Save the submitted drawing as an SVG file.
canvas.save(output / "hello_world.svg")
