# 5.7 Projected layers: a material and probe

Project components separately when explicit illustration coverage is wanted. Sharing a camera and world coordinates aligns their numerical positions; later Canvas order controls overlap between separate projections.

Group the projected components with labels and leaders for immediate 2D edits. Separate projections do not share a depth buffer or perform cross-scene splitting. Source queries follow the projected Group's current 2D coordinates.

## Runnable examples and output

```{literalinclude} ../../../../examples/tutorial/spatial/projected_layers.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![Material reference beside a separately projected probe and 2D label](../../../../examples/output/tutorial/spatial/projected_layers.svg)

Full source: [projected_layers.py](../../../../examples/tutorial/spatial/projected_layers.py).

---

[Part contents](index.md)
