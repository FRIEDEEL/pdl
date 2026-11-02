# 5.1 Project 3D, then draw in 2D

Import 3D objects explicitly from `pdl.extensions.spatial`; they are not root-level drawing shortcuts.

Build right-handed 3D coordinates and solids, select a camera, then explicitly call Scene3D.project. The result is an ordinary 2D ProjectedScene Group that can be combined with core Entities and sent to either backend.

Source vertex and face-center indices remain available independently of paint order. Subsequent 2D edits update those numerical queries and visible members together; the source 3D scene stays unchanged.

## Runnable examples and output

```{literalinclude} ../../../../examples/tutorial/spatial/projection.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![A projected cube with a 2D legend](../../../../examples/output/tutorial/spatial/projection.svg)

Full source: [projection.py](../../../../examples/tutorial/spatial/projection.py).

---

[Part contents](index.md)
