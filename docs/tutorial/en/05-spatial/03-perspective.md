# 5.3 Perspective projection

PerspectiveCamera applies pinhole projection with explicit distance, focal length, and near threshold. Geometry at or behind the near threshold raises an error; no automatic clipping is performed.

Perspective plane curves and glyphs are subdivided into vector paths with a projected control-hull tolerance of 0.02 output millimeters before later 2D scaling. Curved solids and images require the documented orthographic/native workflows. A separate 2D legend remains ordinary text.

## Runnable examples and output

```{literalinclude} ../../../../examples/tutorial/spatial/perspective.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![Orthographic and perspective plane artwork and D10](../../../../examples/output/tutorial/spatial/perspective.svg)

Full source: [perspective.py](../../../../examples/tutorial/spatial/perspective.py).

---

[Part contents](index.md)
