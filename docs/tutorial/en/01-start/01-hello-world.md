# 1.1 Your first picture

Create a rectangle and a literal text label, add them to a Canvas, then save SVG. Drawing factories such as `rectangle(...)` and `text(...)` return Entity objects that own their geometry and optional Style.

From the repository root, select Python 3.12 or later with pyenv and run `uv sync`. Run this example with `uv run python -m examples.tutorial.basics.hello_world`. Its complete source includes the output directory and `canvas.save(...)` call. A usable system font is required; this SVG example uses no TeX compiler.

## Runnable examples and output

```{literalinclude} ../../../../examples/tutorial/basics/hello_world.py
:language: python
```

![hello world](../../../../examples/output/tutorial/basics/hello_world.svg)

Full source: [hello_world.py](../../../../examples/tutorial/basics/hello_world.py).

---

[Part contents](index.md)
