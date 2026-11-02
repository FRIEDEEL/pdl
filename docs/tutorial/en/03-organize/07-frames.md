# 3.7 Reference frames

Frame is a pure origin-and-basis description. Create it explicitly and call point/vector/coordinates for numerical conversion. Ordinary shapes have world coordinates and no implicit frame.

`frame_axes(frame)` creates an explicit drawable Group. Its current basis and visual members transform together; its `.frame` provides the current pure description. The original immutable Frame remains unchanged. Gather can explicitly select the axes Entity and a shape to move both.

## Runnable examples and output

```{literalinclude} ../../../../examples/tutorial/geometry/reference_frames.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![Fixed frame on the left and explicitly rotated frame on the right](../../../../examples/output/tutorial/geometry/reference_frames.svg)

Full source: [reference_frames.py](../../../../examples/tutorial/geometry/reference_frames.py).

---

[Part contents](index.md)
