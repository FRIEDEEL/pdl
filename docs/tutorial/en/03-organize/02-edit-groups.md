# 3.2 Edit and dissolve groups

Use Group when several existing entities should become one editable unit. Every instance has at most one direct parent Group. Adding an Entity or
Group preserves its current world placement; a Drawing instead creates an
independent local instance, as in the group introduction.

```{literalinclude} ../../../../examples/tutorial/layout/editable_groups.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![16. Edit and dissolve groups](../../../../examples/output/tutorial/layout/editable_groups.svg)

[Complete runnable example](../../../../examples/tutorial/layout/editable_groups.py)

The left component is captured before editing; the right component is captured
after rotating and moving it. Both body and port move together. The final
`dismiss()` dissolves this grouping level, so the extra port can move alone.
Earlier draw records remain unchanged.

`group.add(instance)` reparents an existing instance; `group.remove(instance)`
detaches a direct member. Both preserve world placement and effective paint.
`dismiss()` promotes direct members into the parent, retaining nested groups.
The retired empty Group rejects further additions. Singular parent transforms
cannot be inverted for reparenting and raise ValueError.

Explicit child styles override group defaults as whole styles. Draw the
outermost Group, not an individual member. To access a port without drawing
it, use `group.child(index)` or a captured child anchor.

Try adding a third part before the first draw, then removing it after rotation.

---

[Part contents](index.md)
