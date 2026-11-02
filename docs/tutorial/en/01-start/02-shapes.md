# 1.2 Draw some shapes

Use drawing factories for circles, rectangles, lines, polylines, polygons, and arcs. Their arguments describe current world coordinates in millimeters. `Circle(...)` returns an Entity; `pdl.author.geometry.Circle(...)` creates the pure description for explicit `Entity(geometry, style=...)` construction.

A Point or a bare geometric description supplies numerical data. Canvas accepts Entities and expandable components. Arc endpoint/angle constructors belong to the pure `Arc` geometry type; wrap their result in an Entity before drawing.

## Runnable examples and output

```{literalinclude} ../../../../examples/tutorial/basics/shapes.py
:language: python
:start-at: from pdl import
:end-before: output =
```

![shapes](../../../../examples/output/tutorial/basics/shapes.svg)

```{literalinclude} ../../../../examples/tutorial/basics/coordinates.py
:language: python
:start-at: from pdl import
:end-before: output =
```

![coordinates](../../../../examples/output/tutorial/basics/coordinates.svg)

Full source: [shapes.py](../../../../examples/tutorial/basics/shapes.py), [coordinates.py](../../../../examples/tutorial/basics/coordinates.py).

---

[Part contents](index.md)
