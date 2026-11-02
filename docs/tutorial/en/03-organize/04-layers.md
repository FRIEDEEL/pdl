# 3.4 Control layer order

Layer belongs to Canvas and controls paint order. Integer assignments bind to a Canvas layer identity at submission; inserting or reordering layers moves already captured records together. Explicit Layer identities belong to one Canvas.

A Group paints contiguously on its highest member layer, preserving member order within the original layers. Assigning a member's layer promotes the operation to its outermost Group with a warning. Gather can select objects across layers without combining their paint order.

## Runnable examples and output

```{literalinclude} ../../../../examples/tutorial/layout/layers.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![18. Control layer order](../../../../examples/output/tutorial/layout/layers.svg)

![Layers, Gather, and Group compared](../../../../examples/output/composition/sandwich.svg)

Full source: [layers.py](../../../../examples/tutorial/layout/layers.py).

---

[Part contents](index.md)
