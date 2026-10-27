# 18. Control layer order

Layers control coverage only. They have no spatial transformations and cannot
be drawn. The Canvas owns an ordered stack; index zero is the bottom layer.

```{literalinclude} ../../../examples/tutorial/layout/layers.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![18. Control layer order](../../../examples/output/tutorial/layout/layers.svg)

[Complete runnable example](../../../examples/tutorial/layout/layers.py)

Although red is submitted first, its foreground layer places it above gold and
blue. Within a layer, submission order is stable. `set_layer(layer)` and
`layer.add(instance)` assign membership without drawing anything.

`set_layer(1)` resolves to the current Canvas index on the next draw, then binds
the instance to that Layer identity. Prefer `canvas.layers[1]` when selecting a
layer before drawing. `insert_below`/`insert_above` insert between adjacent
layers without changing existing assignments; `move_below`/`move_above` reorder
the layers, including existing captured records.

Read `middle.upper` to get its immediate higher neighbor (`foreground` here),
and `middle.lower` to get its lower neighbor (`background`). At the top/bottom,
or before a Layer joins a stack, the missing neighbor is `None`. Reading these
properties never creates layers; they reflect the current order after insertion
or movement.

There is no active-layer counter. `Layer()` creates an independent identity
whose requested initial position is zero; it does not automatically append a
new top layer. Use explicit `insert_above`/`insert_below` for that intent.

Changing an object's layer affects future draw records; old records keep their
captured layer identity. A Layer belongs to one Canvas. Separate `Layer(1)`
instances are independent identities; use Canvas indexing for canonical lookup.

A Group occupies one layer. Grouping across layers chooses the highest member
layer unless `Group(..., layer=...)` specifies another. Members retain their
old bottom-to-top order inside the group, with argument order breaking ties.
External objects can no longer sandwich its members. Dismissed members retain
the current group layer, not their original layers.

`layer.to_gather()` captures current top-level members for spatial commands.
It includes assigned objects even if not drawn, and does not select old Canvas
snapshots. A Gather can cross layers. Setting a grouped child's layer promotes
the whole outermost Group with a warning.

Try moving foreground below background before saving.


## The sandwich case

![Layers, Gather, and Group compared](../../../examples/output/composition/sandwich.svg)

[Complete runnable source](../../../examples/composition/sandwich.py)

1. Base, middle, and lid occupy three layers. Each plate is itself a Group,
   keeping its bolts and label together.
2. Gather selects base and lid across layers and shifts them right. Their
   components move together, while the middle stays between their layers.
3. Replacing that selection with a Group raises both plates to the highest
   member layer. The base now covers the middle at the lower overlap.

Use Gather to preserve the sandwich; use Group when the selected parts should
become one indivisible spatial and coverage unit.

[Compare Group, Layer, and Gather](groups-layers-gathers.md)
