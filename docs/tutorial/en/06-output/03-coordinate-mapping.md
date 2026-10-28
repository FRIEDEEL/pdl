# 6.3 Draw in a local coordinate system

This section concerns explicit authoring coordinates and per-canvas mappings.
Use Frame for independent operation references; assigning `object.frame` does
not place its geometry in that frame. `in_space` selects coordinate placement.

Imagine drawing a small part that is tilted relative to the page. Rather than
recalculating every coordinate, give the part its own coordinate system.

```{literalinclude} ../../../../examples/tutorial/geometry/local_coordinates.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![Gray world axes and blue local axes](../../../../examples/output/tutorial/geometry/local_coordinates.svg)

[Complete runnable example](../../../../examples/tutorial/geometry/local_coordinates.py)

The gray axes belong to the world frame, with the origin at the lower-left
canvas corner. The blue frame starts at world `(25, 15)` and is rotated 30 degrees.
The circle has local center `(10, 0)`, so it lies on the blue x axis. That pair
is measured from the blue origin, not from the canvas corner.

In `translate(...) @ rotate(...)`, the **right-hand matrix acts first**:
rotate local coordinates, then translate their origin. `shape.in_space(local)`
places geometry in that frame. To define another frame inside it, use
`local.child(Transform.translate(...))`.

Coordinates here belong to the authoring layer: they describe how you arranged
the drawing before a canvas fits or exports it. They do not depend on SVG's
internal downward y direction.

## Points and displacements

`local.point(10, 0)` identifies a position in the blue frame.
`local.vector(10, 0)` identifies a displacement along its x axis. Translating a
frame moves a point but does not change a displacement. You can pass an explicit
space point to `move_to` to avoid guessing which frame a coordinate pair belongs to.

`canvas.map(local, matrix)` overrides that frame's placement for this canvas
only. It replaces the frame's local-to-parent matrix; it does not add to it.
Other canvases and the original frame are unchanged.

## Try it

Change `rotate(30)` to `rotate(60)`. The circle stays on the blue x axis.
Then change `Circle((10, 0), ...)` to `Circle((10, 5), ...)`: it moves away from
that axis along local y.

API: {py:class}`pdl.CoordinateSystem`, {py:class}`pdl.SpacePoint`,
{py:class}`pdl.SpaceVector`. See also the [coordinate guide](../../../coordinates.md).


---

[Part contents](index.md)
