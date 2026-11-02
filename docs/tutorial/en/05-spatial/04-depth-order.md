# 5.4 Transparency and depth order

Coverage order is determined within one projection. sort_faces=False preserves input object/face order; centroid uses an approximate center-depth order. Reordering a ProjectedScene copies its members and preserves source-point correspondence.

Projected faces have per-face opacity, and back faces remain available. Whole-face centroid sorting can fail at intersections or cycles; use BSP for its supported polygon-only scenes.

## Runnable examples and output

```{literalinclude} ../../../../examples/tutorial/spatial/depth_order.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![Transparent faces and automatic versus manual paint order](../../../../examples/output/tutorial/spatial/depth_order.svg)

Full source: [depth_order.py](../../../../examples/tutorial/spatial/depth_order.py).

---

[Part contents](index.md)
