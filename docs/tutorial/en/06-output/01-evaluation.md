# 6.1 From your objects to an image

A position query evaluates current dependencies and returns a fixed Point. Font/TeX tools run only when the operation needs metrics or outlines. Immediate Transform edits store the resulting geometry and any explicit paint changes.

Canvas.snapshot captures an ordinary Entity without submitting it. Canvas.add/draw additionally records paint order and fixes effective styles and typography. Later edits, global defaults, or font policies do not relayout existing records. Backends encode the captured Entities; there is no second resolved scene model.

## Runnable examples and output

```{literalinclude} ../../../../examples/tutorial/advanced/snapshots.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![Original label and later moved label](../../../../examples/output/tutorial/advanced/snapshots.svg)

![Fixed original label](../../../../examples/output/tutorial/advanced/snapshots-copy.svg)

Full source: [snapshots.py](../../../../examples/tutorial/advanced/snapshots.py).

---

[Part contents](index.md)
