# 3.1 Reuse a group of objects

Group is an Entity with ordered, single-parent members. Its transforms immediately update current member geometry in world coordinates. Existing members receive the edit; objects added afterward use their supplied current coordinates.

A member's explicit Style wins. A None member style falls back to the closest explicitly styled Group and then its own default. Adding or removing members preserves None. `group.set_style` changes only the Group. The example's body inherits blue paint while its port keeps explicit orange paint.

Native Text/TeX needs fill-only paint. Give labels an explicit fill-only Style when their Group supplies an outlined shape style.

## Runnable examples and output

```{literalinclude} ../../../../examples/tutorial/layout/groups.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![One component reused in two placements](../../../../examples/output/tutorial/layout/groups.svg)

Full source: [groups.py](../../../../examples/tutorial/layout/groups.py).

---

[Part contents](index.md)
