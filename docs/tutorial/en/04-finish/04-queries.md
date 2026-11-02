# 4.4 Measure a drawing

Queries return numbers immediately. Entity bounds/anchors use authoring world coordinates; Canvas.query defaults to final page coordinates. Pass `in_space=WORLD` for authoring results or an explicit Frame for converted coordinates.

Text logical bounds include layout advances and whitespace; ink_bounds requests glyph outlines. Querying can trigger measurement without submitting anything. Use the resulting numbers to build an explicit guide or another Entity.

On an empty fit/auto-size Canvas, bounds queries predict the queried object's
submission placement. Once drawings exist, queries use their current page mapping.
Use `canvas.viewport().output_transform` to inspect that world-to-page mapping.

## Runnable examples and output

```{literalinclude} ../../../../examples/tutorial/geometry/queries.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![Rotated shape and red axis-aligned bounds](../../../../examples/output/tutorial/geometry/queries.svg)

Full source: [queries.py](../../../../examples/tutorial/geometry/queries.py).

---

[Part contents](index.md)
