# 6.3 Draw in a local coordinate system

Use explicit Frame conversions before constructing shapes. Frame.point returns a fixed world position. `canvas.map(WORLD, affine)` selects the final world-to-page mapping without rewriting source Entities.

Canvas query-frame overrides affect explicit SpacePoint/SpaceVector query conversion. They do not move already numerical object coordinates. Fit/auto-size adds the final viewport mapping; `query.from_canvas` converts a page position back through that mapping.

## Runnable examples and output

```{literalinclude} ../../../../examples/tutorial/geometry/local_coordinates.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![Gray world axes and blue local axes](../../../../examples/output/tutorial/geometry/local_coordinates.svg)

Full source: [local_coordinates.py](../../../../examples/tutorial/geometry/local_coordinates.py).

---

[Part contents](index.md)
