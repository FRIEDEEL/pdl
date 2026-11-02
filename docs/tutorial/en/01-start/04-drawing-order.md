# 1.4 Which object is in front?

Canvas captures the current state when an object is submitted. Later submissions cover earlier ones within a Layer. Reversing submission order changes coverage without changing how anchors or positions were computed.

A referenced object is drawn only when explicitly submitted. Later edits require another `add` or `draw` call, which records another independent state.

## Runnable examples and output

```{literalinclude} ../../../../examples/tutorial/layout/circle_first.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![Rectangle painted after the circle](../../../../examples/output/tutorial/layout/circle_first.svg)

```{literalinclude} ../../../../examples/tutorial/layout/rectangle_first.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![Circle painted after the rectangle](../../../../examples/output/tutorial/layout/rectangle_first.svg)

Full source: [circle_first.py](../../../../examples/tutorial/layout/circle_first.py), [rectangle_first.py](../../../../examples/tutorial/layout/rectangle_first.py).

---

[Part contents](index.md)
