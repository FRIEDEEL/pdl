# 1. Your first picture

Let's make a small box containing **Hello world** and save it as an SVG image.
You only need Python and pdl for this example; you do not need a TeX installation.

## Before you start

These first chapters use a local checkout of pdl. Select Python 3.12 or later
with pyenv, open a terminal in the repository root (the folder containing
`pyproject.toml`), and install the project and its development tools:

```sh
uv sync
```

The commands below assume that `uv` and a suitable Python version are already
installed. If font discovery fails, make a system sans-serif font available;
pdl uses one automatically for this label. Its exact appearance can vary between
computers.

## Write and run the script

Save the following as `examples/tutorial/basics/hello_world.py`, or open the
existing file in this checkout. Run it using the command below the code.

```python
from pathlib import Path

from pdl import Canvas, Node, Text

hello = Node(Text("Hello world"), position=(30, 15))

canvas = Canvas(60, 30)
canvas.draw(hello)

output = Path(__file__).resolve().parents[2] / "output" / "tutorial" / "basics"
output.mkdir(parents=True, exist_ok=True)
canvas.save(output / "hello_world.svg")
```

Run from the repository root:

```sh
uv run python examples/tutorial/basics/hello_world.py
```

![hello world](../../../examples/output/tutorial/basics/hello_world.svg)

[Source file](../../../examples/tutorial/basics/hello_world.py)

Open `examples/output/tutorial/basics/hello_world.svg` in a browser.
You should see the words “Hello world” inside a rectangular outline.
The picture above is that SVG, so run the script first if it is missing in your
local Markdown preview. All tutorial images are generated under
`examples/output/`, which is intentionally excluded from Git.

## What each part does

`Text("Hello world")` creates the words. `Node(...)` puts a box around them,
leaving a little space between the text and the border. You do not need to
calculate the box's width yourself.

`position=(30, 15)` places the **center of the node** 30 mm to the right and
15 mm up from the lower-left corner of the canvas.

`Canvas(60, 30)` creates a drawing area 60 mm wide and 30 mm high. For these
examples, x increases to the right and y increases upward. Coordinates and
shape dimensions are in millimeters.

`canvas.draw(hello)` adds the node to the picture. Creating a node alone does
not put it on the canvas. `canvas.save(...)` writes the SVG file.

The last three lines choose an output folder next to the other example outputs,
create it if necessary, and save the picture there. You can instead use
`canvas.save("hello_world.svg")` to save in your terminal's current directory.

## Try a small change

Replace `"Hello world"` with `"My first drawing"` and run the script again.
The box becomes wider to fit the new text; its center stays at `(30, 15)`.
Then try `position=(30, 22)`: the node moves upward.
The canvas size stays fixed, so content outside it is clipped.

Next: [draw a triangle, a rectangle, and a circle](02-shapes.md).
