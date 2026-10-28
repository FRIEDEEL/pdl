# 4.3 Choose what fits on the page

A canvas can keep a fixed window, fit all content into a fixed size, or choose
its own dimensions. Use the same rectangle and circle to compare these modes.

## Keep a fixed window: clip

```{literalinclude} ../../../../examples/tutorial/advanced/viewport_clip.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![Fixed viewport clips the circle](../../../../examples/output/tutorial/advanced/viewport_clip.svg)

[Complete runnable example](../../../../examples/tutorial/advanced/viewport_clip.py)

The circle is mostly beyond the 60 mm right edge. `clip` is the default:
it does not move or shrink the objects to bring them into view. Padding has
no effect in this mode.

## Fit everything into a fixed size

```{literalinclude} ../../../../examples/tutorial/advanced/viewport_fit.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![Fit shows all content in the fixed viewport](../../../../examples/output/tutorial/advanced/viewport_fit.svg)

[Complete runnable example](../../../../examples/tutorial/advanced/viewport_fit.py)

`fit` keeps the 60 × 40 mm canvas, scales content uniformly, and centers it
with the requested margin. The rectangle and circle retain their relative arrangement.

## Choose the page size from the content

```{literalinclude} ../../../../examples/tutorial/advanced/viewport_auto_size.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![Auto-size preserves scale and changes canvas dimensions](../../../../examples/output/tutorial/advanced/viewport_auto_size.svg)

[Complete runnable example](../../../../examples/tutorial/advanced/viewport_auto_size.py)

`auto_size` keeps the geometry's scale and chooses the output dimensions from
content plus padding. The supplied width and height do not constrain it; you
can instead write `Canvas(mode="auto_size", padding=4)`.

Text scales along with geometry; stroke widths remain in Canvas millimeters.
Fitting uses layout bounds and conservative stroke margins, not exact painted
outlines. That may leave extra space around some shapes or text.

## Try it

Increase the circle's x coordinate in each example. Under clip it disappears
farther outside the window; under fit the content shrinks; under auto-size the
page becomes wider. Query final Canvas positions only after defining the paint list.

API: {py:class}`pdl.Canvas`.


---

[Part contents](index.md)
