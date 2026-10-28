# 2.3 Copy and capture

Transforms mutate the object and return it. Use `copy()` for another editable
object; modifying either copy does not change the other. A Group copy includes
independent members.

```{literalinclude} ../../../../examples/tutorial/geometry/copy_and_capture.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![Original gray record, moved blue object, independent orange copy](../../../../examples/output/tutorial/geometry/copy_and_capture.svg)

[Complete source](../../../../examples/tutorial/geometry/copy_and_capture.py)

The gray circle records the original position. The blue circle is the same
object after moving; the orange copy keeps its independent position.

| Operation | Result |
| --- | --- |
| `object.copy()` | Independent editable object |
| `object.anchor(...)` | Description of the anchor at this call; measurement can wait |
| `canvas.draw(object)` | Recorded description; later object edits do not change it |
| `canvas.snapshot(object)` | Ordinary Drawing with fixed authoring placement and typography |

References and `draw` capture descriptions, not necessarily numeric font metrics.
The evaluation part explains `resolve` in detail. `frame.visualize()` also creates
an independent drawable snapshot, as explained in the organization part.

[Part contents](index.md)
