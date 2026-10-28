# 2.2 Move, rotate, and scale

So far we have placed shapes by supplying coordinates to their constructors.
Shapes already inherit {py:class}`pdl.Entity`; move them directly with method calls.

## Move a rectangle

```{literalinclude} ../../../../examples/tutorial/geometry/translation.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![Old outline and translated rectangle](../../../../examples/output/tutorial/geometry/translation.svg)

[Complete runnable example](../../../../examples/tutorial/geometry/translation.py)

`translate(25, 10)` moves the box 25 mm right and 10 mm up. It modifies the
Entity. The first draw call captured its old state, so the gray outline stays
where it was; the second draw records its new state. This gives us a useful
before/after picture without calculating new vertices.

`move_to((x, y))` is different: it places the transformed local bounds center
at a target, rather than adding a displacement.

## Choose a rotation center

```{literalinclude} ../../../../examples/tutorial/geometry/rotation.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![Rectangle rotated around its marked center](../../../../examples/output/tutorial/geometry/rotation.svg)

[Complete runnable example](../../../../examples/tutorial/geometry/rotation.py)

The red dot is the pivot `(25, 20)`. Positive angles turn counterclockwise.
The gray outline shows the old position. Without `about=...`, direct shapes rotate around their own center. Use an explicit
world point when the box should also orbit another location.

## Stretch a circle

```{literalinclude} ../../../../examples/tutorial/geometry/scaling.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![A circle stretched into an ellipse](../../../../examples/output/tutorial/geometry/scaling.svg)

[Complete runnable example](../../../../examples/tutorial/geometry/scaling.py)

The x factor is 2 and the y factor is 0.75, so the result is an ellipse.
A single factor gives uniform scaling. The about argument keeps the pivot
fixed. Geometry and text scale; stroke widths remain in Canvas millimeters.

These methods return the same Entity, so calls can be chained. Operations use world coordinates. To compare transform order, use the same
explicit fixed pivot in both sequences: translation then rotation around that
pivot generally differs from the reverse. Default center rotation follows the
object's current center, so that example does not demonstrate the same rule. `reflect(angle, origin=...)` mirrors about a
line; `Transform.shear(...)` provides shear for `entity.apply_transform(...)`.

## Try it

Change the rotation to `-30`. Then try a different `about`, such as `(15, 15)`.
Watch both the box's orientation and its position. Keep the gray outline as a reference.

API: {py:class}`pdl.Entity`, {py:class}`pdl.Transform`.


---

[Part contents](index.md)
