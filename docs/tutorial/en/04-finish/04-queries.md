# 4.4 Measure a drawing

Anchors let us describe relationships without immediately calculating numbers.
Sometimes we need actual numbers: for example, to inspect the width of a
rotated shape. Use a canvas query for that job.

```{literalinclude} ../../../../examples/tutorial/geometry/queries.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![Rotated shape and red axis-aligned bounds](../../../../examples/output/tutorial/geometry/queries.svg)

[Complete runnable example](../../../../examples/tutorial/geometry/queries.py)

The red rectangle is the smallest axis-aligned box around the rotated
geometry. Its sides stay parallel to the world axes; it is not a rotated copy
of the original rectangle. The terminal also prints the center `(30.0, 20.0)`.

`in_space=WORLD` explicitly requests authoring world coordinates. Omitting it
returns final Canvas coordinates, which can differ under `fit` or a canvas
mapping. The bounds exclude stroke width. For text, ordinary bounds use the
layout box; `ink_bounds` uses visible glyph outlines instead.

A Bounds value exposes `left`, `bottom`, `right`, `top`, `width`, and `height`.
Its `anchor(...)` returns a numerical Point. To evaluate a deferred anchor,
use `canvas.query().point(reference, in_space=WORLD)`.

Queries do not draw their targets. In the example, only the explicit draw calls
add the shape and frame. Also, a numerical result is a snapshot: the red frame
will not follow later changes unless you query and rebuild it again.

With fitted canvases, define the paint list before querying final Canvas
coordinates, because that list determines the fit. Converting back with
`query().from_canvas(...)` gives a fixed authoring point, not an anchor dependency.
Inverse conversions through a singular transform raise ValueError.

## Try it

Change the rotation from 30 to 60 degrees. Rerun and compare the bounds' width
and height. An empty Bounds has `is_empty=True` and no valid anchor.

API: {py:class}`pdl.Query`, {py:class}`pdl.Bounds`.


---

[Part contents](index.md)
