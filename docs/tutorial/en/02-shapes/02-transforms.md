# 2.2 Move, rotate, and scale

Transform operations take effect immediately. Translation rewrites positions; rotation and scaling use the Entity reference point by default. Pass `origin=` to select another pivot. Rectangle uses its lower-left reference, Circle its center, Path its first move, and Text/TeX their baseline.

Conversion decisions belong to the transform package. A stretched circle becomes a Path while its Entity identity remains the same. Stroke width stays fixed by default. Uniform `Rescale(factor, include_linewidth=True)` or `entity.rescale(..., include_linewidth=True)` also changes line width; nonuniform Scaling has no such option.

## Runnable examples and output

```{literalinclude} ../../../../examples/tutorial/geometry/translation.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![Old outline and translated rectangle](../../../../examples/output/tutorial/geometry/translation.svg)

```{literalinclude} ../../../../examples/tutorial/geometry/rotation.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![Rectangle rotated around its marked center](../../../../examples/output/tutorial/geometry/rotation.svg)

```{literalinclude} ../../../../examples/tutorial/geometry/scaling.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![A circle stretched into an ellipse](../../../../examples/output/tutorial/geometry/scaling.svg)

Full source: [translation.py](../../../../examples/tutorial/geometry/translation.py), [rotation.py](../../../../examples/tutorial/geometry/rotation.py), [scaling.py](../../../../examples/tutorial/geometry/scaling.py).

---

[Part contents](index.md)
