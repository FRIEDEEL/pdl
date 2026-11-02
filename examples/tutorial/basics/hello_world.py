from pathlib import Path

from pdl import Canvas, rectangle, text

box = rectangle((10, 7), width=40, height=16)
hello = text("Hello world", position=(30, 13), align="center")

canvas = Canvas(60, 30)
canvas.draw(box)
canvas.draw(hello)

output = Path(__file__).resolve().parents[2] / "output" / "tutorial" / "basics"
output.mkdir(parents=True, exist_ok=True)
canvas.save(output / "hello_world.svg")
