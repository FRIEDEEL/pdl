# 2.1 Draw your own outlines and curves

Import `Path` from `pdl.author.geometry` to construct geometry explicitly. This example aliases it as PathGeometry. It is a mutable builder. `move_to` starts a subpath, `line_to` adds a segment, `quadratic_to` uses one control point, and `cubic_to` uses two. `close()` adds the closing edge and restores the subpath's starting cursor.

Create an Entity from the completed builder to attach paint and move the whole object. The builder's `move_to` constructs commands; Entity.move_to changes the object's position. Coordinates are absolute world values. New subpaths do not connect automatically; fills implicitly close open subpaths while strokes remain open.

## Runnable examples and output

```{literalinclude} ../../../../examples/tutorial/geometry/outline.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![A custom closed outline](../../../../examples/output/tutorial/geometry/outline.svg)

```{literalinclude} ../../../../examples/tutorial/geometry/curve.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![A cubic curve and two control handles](../../../../examples/output/tutorial/geometry/curve.svg)

Full source: [outline.py](../../../../examples/tutorial/geometry/outline.py), [curve.py](../../../../examples/tutorial/geometry/curve.py).

---

[Part contents](index.md)
