# 2.4 Multiple subpaths and holes

Independent subpaths support holes and compound outlines. Nonzero fill uses winding; evenodd fill counts crossings. Choosing a fill rule does not add stroke edges to open subpaths.

`PathGeometry.extend(...)` appends a path-compatible geometric description. Use pure geometries inside builders, then create an Entity for drawing. Affine Bézier control-point mapping is exact; circular/elliptical path lowering uses cubic approximation with segments spanning at most 45 degrees.

## Runnable examples and output

```{literalinclude} ../../../../examples/tutorial/advanced/fill_rules.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![Nonzero fill on the left, evenodd on the right](../../../../examples/output/tutorial/advanced/fill_rules.svg)

Full source: [fill_rules.py](../../../../examples/tutorial/advanced/fill_rules.py).

---

[Part contents](index.md)
