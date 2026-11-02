# 5.2 Put artwork in a plane

Plane3D supplies an explicit origin and two 3D basis vectors for 2D artwork. Projection determines actual 2D geometry. Text retains native form under orientation-preserving similarities. TeX retains source under translation/rotation; scaling and other affine plane deformations produce measured outlines.

Artwork is grouped with its surface before coverage ordering. It is not automatically clipped or lit. Use centroid ordering explicitly for scenes with artwork, and keep artwork within its intended face boundary.

## Runnable examples and output

```{literalinclude} ../../../../examples/tutorial/spatial/plane_text.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![Native text on flat and inclined planes](../../../../examples/output/tutorial/spatial/plane_text.svg)

Full source: [plane_text.py](../../../../examples/tutorial/spatial/plane_text.py).

---

[Part contents](index.md)
