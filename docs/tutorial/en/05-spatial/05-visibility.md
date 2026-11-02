# 5.5 Intersections and visibility

BSP splits intersecting polygon faces into back-to-front fragments and triangulates supported concave loops. Source-face correspondence remains available, and new cut edges are not stroked.

Auto selects BSP for polyhedra without artwork; unsupported content uses a warned centroid fallback. Explicit bsp rejects unsupported scenes. Floating tolerances, fragment budgets, and a tree-depth safety limit bound the algorithm; it supplies diagram visibility rather than solid booleans or exact arithmetic.

## Runnable examples and output

```{literalinclude} ../../../../examples/tutorial/spatial/visibility.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![Same intersecting panels: centroid reference and BSP visibility](../../../../examples/output/tutorial/spatial/visibility.svg)

![Four centroid/BSP comparisons](../../../../examples/output/spatial/visibility.svg)

Full source: [visibility.py](../../../../examples/tutorial/spatial/visibility.py).

---

[Part contents](index.md)
