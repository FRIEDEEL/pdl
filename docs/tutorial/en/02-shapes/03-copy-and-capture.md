# 2.3 Copy and capture

Entity.copy creates independent geometry and Group members and detaches the root from its parent and layer identity. Use it to keep editable versions. Canvas submission captures another independent state; moving the original later does not change a recorded drawing.

Entity construction directly retains a supplied geometry. Explicitly sharing a mutable Path shares direct builder edits. A Transform replaces only the target Entity's geometry; use Gather for deliberate multi-object edits.

## Runnable examples and output

```{literalinclude} ../../../../examples/tutorial/geometry/copy_and_capture.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![Original gray record, moved blue object, independent orange copy](../../../../examples/output/tutorial/geometry/copy_and_capture.svg)

Full source: [copy_and_capture.py](../../../../examples/tutorial/geometry/copy_and_capture.py).

---

[Part contents](index.md)
