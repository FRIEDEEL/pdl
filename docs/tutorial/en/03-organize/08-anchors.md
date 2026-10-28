# 3.8 Attach objects and connect nodes

Instead of guessing a label's width, ask for a named point on its boundary.
An **anchor** gives you such a point: `east` is on the right, `west` on the left,
`north` at the top, and `center` in the middle.

## Connect two labels

```{literalinclude} ../../../../examples/tutorial/layout/anchors.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![Two nodes joined at their boundary anchors](../../../../examples/output/tutorial/layout/anchors.svg)

[Complete runnable example](../../../../examples/tutorial/layout/anchors.py)

The Finish node's center is 35 mm to the right of the Start node's east anchor.
That is a center offset, not a 35 mm gap between the two outlines.
The connection joins east to west; the red guide dots show its endpoints.
`Connection` adds an arrowhead at its end by default. Set `arrow_end=False`
for a plain connector, or supply `via=((x, y), ...)` for a manually chosen route.
It does not find a route around other objects.

The anchor call measures the current node and returns a fixed numerical point.
Drawing the link first keeps it behind the nodes, independently of measurement order.

## What happens after moving an Entity?

```{literalinclude} ../../../../examples/tutorial/layout/captured_anchors.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![An old attachment stays below; a new one uses the moved box](../../../../examples/output/tutorial/layout/captured_anchors.svg)

[Complete runnable example](../../../../examples/tutorial/layout/captured_anchors.py)

The orange circle was attached before the box moved upward. It keeps the
captured old position. The green circle was attached afterward and uses the
new position. An Entity anchor is a fixed numerical point calculated at the call;
it does not track later edits.

To transform a connected assembly together, use the Group operations introduced earlier.

For a rotated object, `east` means its local right-side anchor transformed with
it, not necessarily the rightmost point of its final axis-aligned box.
Use explicit frame vectors with `anchor + frame.vector(...).resolve()` when an
offset's direction should follow a particular frame.

## Try it

Replace `"Start"` with `"A longer starting label"`. The right node and link
adjust to the newly measured right edge. Increase the canvas width if needed.

API: {py:class}`pdl.Connection`, {py:meth}`pdl.Entity.anchor`.


---

[Part contents](index.md)
