# 2. Construct and transform

In Part 1, you created drawing objects and submitted them to a Canvas. Before
constructing paths and transforming shapes, look at what those objects contain.
This part introduces three concepts: **Geometry**, **Style**, and **Entity**.

## What happens when you call rectangle()?

The [shape example in Part 1](../01-start/02-shapes.md) contains this line:

```{literalinclude} ../../../../examples/tutorial/basics/shapes.py
:language: python
:start-at: rectangle_entity =
:end-before: circle_entity =
```

`rectangle` is a factory function. It first creates a `Rectangle` geometric
description with a lower-left corner at `(40, 10)`, a width of 25 mm, and a height
of 20 mm. It then creates an `Entity` holding that description and returns the
Entity. The variable `rectangle_entity` therefore refers to a drawing object,
which you can edit and submit with `canvas.draw(rectangle_entity)`.

The function does not submit anything to a Canvas. It also leaves the Entity's
`style` as `None` when you omit `style=`; it does not construct an explicit Style
for the object. A standalone rectangle with an unset style uses its default
black outline and no fill when drawn.

## Geometry, Style, and Entity

| Concept | What it describes | In this example |
| --- | --- | --- |
| Geometry | The current shape, dimensions, and position, without paint | A `Rectangle` with an origin, width, and height |
| Style | Paint settings such as stroke, fill, and line width | An orange fill and a 0.5 mm outline |
| Entity | A drawing object holding geometry and an optional Style, with operations such as moving the object | The object passed to `canvas.draw(...)` |

Geometry is the name for the geometric descriptions, rather than a common class
you must instantiate. Here the concrete geometry class is `Rectangle`. Lowercase
`rectangle(...)` creates a drawing Entity; uppercase `Rectangle(...)` creates
only the geometric description.

The two construction forms below produce equivalent rectangles:

```{literalinclude} ../../../../examples/tutorial/geometry/object_model.py
:language: python
:start-after: "# construction-start"
:end-before: "# construction-end"
```

`Entity(geometry)` retains the supplied geometry, accessible through
`explicit_rectangle.geometry`. It does not copy it or submit it to a Canvas.
Both construction forms leave the optional Style unset. A bare `Rectangle`
description can be queried numerically, but wrap it in an Entity before drawing.

## Add a Style

In [Part 1's color example](../01-start/03-stroke-and-fill.md), you supplied an
orange Style to `canvas.draw(rectangle_entity, orange)`. You can also store that
Style on the drawing object itself, either through the factory or directly:

```{literalinclude} ../../../../examples/tutorial/geometry/object_model.py
:language: python
:start-after: "# style-start"
:end-before: "# style-end"
```

`orange` describes the paint, while `geometry` describes the rectangle. The
Entity `editable` holds both: `editable.geometry` is the supplied Rectangle and
`editable.style` is the supplied Style. The factory performs the same wrapping
in one call. Its result has equivalent geometry and paint, but is a separate
object with its own geometric description.

A Style is an immutable value. To change an Entity's paint, create another Style
and pass it to `set_style(...)`. Omitting an Entity's Style is different from
setting `stroke=None` or `fill=None` inside a Style: those fields explicitly
disable the outline or fill. A Style passed to `canvas.draw(...)` applies to
that submission and leaves the source Entity's stored Style unchanged.

## draw() makes an impression of the current state

Think of `canvas.draw(editable)` as making an impression on the Canvas. At that
moment, it captures the object's current geometry and effective paint. You can
continue editing the source Entity, its geometric description, or its assigned
Style afterward; those edits do not change the impression already on the Canvas.
Saving the Canvas uses its submitted records rather than rereading the source
objects.

This example draws the same Entity twice, with edits between the two calls:

```{literalinclude} ../../../../examples/tutorial/geometry/object_model.py
:language: python
:start-after: "# capture-start"
:end-before: "# capture-end"
```

The first call records the orange 25 × 20 mm rectangle at `(40, 10)`.
`geometry.width = 15` then changes the description held by the source Entity.
`translate(30, 15)` moves that Entity 30 mm right and 15 mm up, and `set_style`
replaces its paint with blue. None of these edits changes the first record.
Only the second `draw` adds the narrower blue rectangle at `(70, 25)`.
If you omit that second call, the saved picture contains only the first orange
rectangle, regardless of the later source edits.

![First orange impression and second narrower blue impression of the same Entity](../../../../examples/output/tutorial/geometry/object_model.svg)

Full source: [object_model.py](../../../../examples/tutorial/geometry/object_model.py).
Run it with `uv run python -m examples.tutorial.geometry.object_model`.
[Copy and capture](03-copy-and-capture.md) returns to independent editable copies
and submission capture in more detail.

## In this part

```{toctree}
:maxdepth: 1

01-paths
02-transforms
03-copy-and-capture
04-fill-rules
```

[Part contents](../index.md)
