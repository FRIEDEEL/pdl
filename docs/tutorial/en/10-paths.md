# 10. Draw your own outlines and curves

Use {py:class}`pdl.Path` when a built-in shape is not enough. A path is a list
of instructions: move the pen, draw a segment, bend a curve, or close an outline.
It has no color until you draw it with a style.

## Join a few points

```{literalinclude} ../../../examples/tutorial/geometry/outline.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![A custom closed outline](../../../examples/output/tutorial/geometry/outline.svg)

[Complete runnable example](../../../examples/tutorial/geometry/outline.py)

`move_to` chooses the starting point without drawing. Each `line_to` adds a
straight segment. `close()` draws the final edge back to the start.
These methods modify the path and return it, allowing the chain above.

All positions are absolute local coordinates. Starting another `move_to`
begins a separate subpath without connecting it to the previous one.
An open subpath can be filled as though it were closed, but its stroke does
not gain a closing edge unless you call `close()`.

## Bend a curve

```{literalinclude} ../../../examples/tutorial/geometry/curve.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![A cubic curve and two control handles](../../../examples/output/tutorial/geometry/curve.svg)

[Complete runnable example](../../../examples/tutorial/geometry/curve.py)

The curve starts at `(10, 10)` and ends at `(45, 10)`. Its two control points
are `(10, 35)` and `(45, 35)`, marked by small circles. The gray lines show
the handles: the curve leaves the start toward the first control point and
arrives at the end from the direction of the second. It does not generally
pass through either control point.

`quadratic_to(control, end)` is the one-control-point alternative.
Lines and curves require a preceding `move_to`. `Path.arc(Arc(...))` can append
an arc; it joins to the arc's start if necessary and uses a cubic approximation.

## Try it

Lower the first control point from `(10, 35)` to `(10, 20)`, updating its guide
line and marker too. The left part of the curve becomes flatter.

After `canvas.draw(path)`, editing the path does not change that recorded draw.
Draw it again to record the new state. [Multiple subpaths and fill rules](15-fill-rules.md)
are covered after the rendering chapters.

API: {py:class}`pdl.Path`, {py:class}`pdl.Arc`.

---

[Previous: Reusable groups](09-groups.md) · [Next: Geometry queries](11-geometry-queries.md)
