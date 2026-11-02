# 3.6 Non-painting reference points

A Point is an immutable numerical reference. An Entity keeps a reference point used by default rotation/scaling; set_reference changes this pivot without moving the geometry. `move_to(position)` aligns that reference, while `anchor=` selects a logical bounds anchor.

Reference points and visual markers are separate choices. Submit a Circle Entity if the point should be visible. Position queries return fixed numbers; subsequent edits do not create live attachments.

## Runnable examples and output

```{literalinclude} ../../../../examples/tutorial/layout/reference_points.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![Rectangle rotated about a marked reference point](../../../../examples/output/tutorial/layout/reference_points.svg)

Full source: [reference_points.py](../../../../examples/tutorial/layout/reference_points.py).

---

[Part contents](index.md)
