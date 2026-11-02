# 1.1 Your first picture

Create a framed "Hello world" label and save it as SVG. The two main steps are
to create the drawing objects and submit them to a Canvas.

From the repository root, select Python 3.12 or later with pyenv and run `uv sync`. Run this example with `uv run python -m examples.tutorial.basics.hello_world`. Its complete source includes the output directory and `canvas.save(...)` call. A usable system font is required; this SVG example uses no TeX compiler.

## Complete example

```{literalinclude} ../../../../examples/tutorial/basics/hello_world.py
:language: python
```

## Create the drawing objects

`text("Hello world")` creates a text label and assigns it to `label`.
`Node(label, position=(30, 15))` places that label inside a rectangular border,
which is sized to fit the text. The resulting framed label is assigned to `hello`.
Its center is at `(30, 15)`, in millimeters.

These calls create objects that you can use in a drawing. Creating an object
does not automatically put it on a Canvas.

## Submit to a Canvas and save

`Canvas(60, 30)` creates a drawing area 60 mm wide and 30 mm high. Its origin is
at the lower-left corner, so `(30, 15)` puts the node in the middle of the page.

`canvas.draw(hello)` submits the framed label to this Canvas. This is the step
that includes it in the picture: without the call, saving this Canvas would
produce an empty drawing.

Finally, the example creates an output directory and calls `canvas.save(...)`.
The SVG file is written to `examples/output/tutorial/basics/hello_world.svg`.
Open it in a browser to see the result below.

## Result

![Hello world label inside a rectangular border](../../../../examples/output/tutorial/basics/hello_world.svg)

Full source: [hello_world.py](../../../../examples/tutorial/basics/hello_world.py).

---

[Part contents](index.md)
