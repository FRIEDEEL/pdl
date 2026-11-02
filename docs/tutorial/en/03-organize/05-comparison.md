# 3.5 Group, Layer, and Gather: structure, order, and selection

Group owns an assembly, Layer orders captured coverage, and Gather selects existing objects for explicit commands. A Group retains member identities and style fallback; its current coordinates are edited immediately. A Layer has no spatial transform. A Gather retains membership and permits overlap.

For `Gather(a, b)` and `Gather(b, c)`, B receives edits from both selections in call order. One operation deduplicates identities; separate operations each apply. Relative positions are not protected against later edits through another selection.

| Concept | Ownership | Spatial edits | Paint |
| --- | --- | --- | --- |
| Group | One parent per member | Current family edited together | Explicit ancestor fallback |
| Gather | None; overlaps allowed | Explicit targets, deduplicated per operation | Set exactly selected objects |
| Layer | Canvas order identity | No transform | Orders captured submissions |

## Runnable examples and output

```{literalinclude} ../../../../examples/tutorial/layout/shared_gathers.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![Two overlapping Gathers change one another's relative arrangement](../../../../examples/output/tutorial/layout/shared_gathers.svg)

Full source: [shared_gathers.py](../../../../examples/tutorial/layout/shared_gathers.py).

---

[Part contents](index.md)
