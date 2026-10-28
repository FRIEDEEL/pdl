# 3.6 Non-painting reference points

`ReferencePoint` is an Entity used for positioning and pivots. It can be moved,
copied, and included in Group or Gather. It produces no paint and contributes
nothing to visible bounds, viewport fitting, or occlusion.

```{literalinclude} ../../../../examples/tutorial/layout/reference_points.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![Rectangle rotated about a marked reference point](../../../../examples/output/tutorial/layout/reference_points.svg)

[Complete source](../../../../examples/tutorial/layout/reference_points.py)

`pivot.position` is its current numeric world point. The red marker is an
explicit Circle; drawing the reference itself does not show anything. The gray
outline retains the original rectangle.

Moving the box alone does not move the reference. Use `Gather(box, pivot)` for
an explicit shared operation. A Frame adds two basis vectors to an origin;
the next section explains that reference.

[Part contents](index.md)
