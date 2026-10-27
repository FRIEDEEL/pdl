from pathlib import Path

from pdl import Canvas, Node, Text

hello = Node(Text("Hello world"), position=(30, 15))

canvas = Canvas(60, 30)
canvas.draw(hello)

output = Path(__file__).resolve().parents[2] / "output" / "tutorial" / "basics"
output.mkdir(parents=True, exist_ok=True)
canvas.save(output / "hello_world.svg")
