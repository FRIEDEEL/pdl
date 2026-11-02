# 4.1 Fill with gradients and opacity

LinearGradient and RadialGradient use ordered opaque RGB stops. Initial coordinates are normalized to the object's bounds. A transform bakes the gradient's current coordinate frame alongside geometry so the painted direction and shape remain aligned.

Gradients are fills. Native Text/TeX require solid fills. Opacity applies per leaf; overlapping members are painted independently, and a Group does not establish an isolated transparency surface.

## Runnable examples and output

```{literalinclude} ../../../../examples/tutorial/paint/gradients.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![20. Fill with gradients and opacity](../../../../examples/output/tutorial/paint/gradients.svg)

```{literalinclude} ../../../../examples/tutorial/paint/opacity.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![Opacity](../../../../examples/output/tutorial/paint/opacity.svg)

Full source: [gradients.py](../../../../examples/tutorial/paint/gradients.py), [opacity.py](../../../../examples/tutorial/paint/opacity.py).

---

[Part contents](index.md)
