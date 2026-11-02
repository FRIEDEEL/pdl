# 5.6 Cylindrical surfaces

Sphere, Cylinder, CylinderSurface, and AnnularCylinder provide smooth orthographic diagram shapes. Lighting can generate continuous gradient fills. Surface arcs are lowered through current 2D path geometry.

Curved scenes use centroid/manual ordering rather than polygon BSP. Surface transforms support their documented similarity restrictions. Compare limiting camera angles and the unmodified reference shown beside the assembled result.

## Runnable examples and output

```{literalinclude} ../../../../examples/tutorial/spatial/cylinder_surface.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![An open half-cylinder viewed from its interior](../../../../examples/output/tutorial/spatial/cylinder_surface.svg)

```{literalinclude} ../../../../examples/tutorial/spatial/washer.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![A washer with its central bore open](../../../../examples/output/tutorial/spatial/washer.svg)

![Above, below, side and axial views of washers and open surfaces](../../../../examples/output/spatial/material_probe-views.svg)

Full source: [cylinder_surface.py](../../../../examples/tutorial/spatial/cylinder_surface.py), [washer.py](../../../../examples/tutorial/spatial/washer.py).

---

[Part contents](index.md)
