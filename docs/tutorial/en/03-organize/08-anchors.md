# 3.8 Attach objects and connect nodes

Entity.anchor returns a Point from current logical geometry/layout bounds, excluding stroke. Cardinal and diagonal names use the world-aligned rectangle; Node's circular diagonal ports lie on its circular boundary.

Query the source when constructing another object or a Connection. These numerical results and connection endpoints remain fixed when the source is later edited. Recompute and rebuild an attachment when a new position is wanted.

## Runnable examples and output

```{literalinclude} ../../../../examples/tutorial/layout/anchors.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![Two nodes joined at their boundary anchors](../../../../examples/output/tutorial/layout/anchors.svg)

```{literalinclude} ../../../../examples/tutorial/layout/captured_anchors.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![An old attachment stays below; a new one uses the moved box](../../../../examples/output/tutorial/layout/captured_anchors.svg)

Full source: [anchors.py](../../../../examples/tutorial/layout/anchors.py), [captured_anchors.py](../../../../examples/tutorial/layout/captured_anchors.py).

---

[Part contents](index.md)
