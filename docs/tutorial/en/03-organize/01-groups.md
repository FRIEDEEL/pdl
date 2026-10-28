# 3.1 Reuse a group of objects

Our small component is a rectangular body with a circular port. We want to
place it twice and rotate one copy without recalculating its parts.

```{literalinclude} ../../../../examples/tutorial/layout/groups.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![One component reused in two placements](../../../../examples/output/tutorial/layout/groups.svg)

[Complete runnable example](../../../../examples/tutorial/layout/groups.py)

`Group((body, port))` owns these existing objects and preserves their world
placement when adding them. Transforming the Group moves both together.
`copy()` creates another Group with independent members.

`first` is a translated copy. `second` rotates around the explicit world origin,
then translates. The original component is unchanged. A child with an explicit
style uses that whole style; otherwise it inherits the group default.

Draw the outermost Group. Use `second.child(1)` to obtain a captured description
of its port for anchors and connections; this does not draw the port separately.

## Try it

Create a third copy and move it elsewhere. Change a member of only that copy;
the other groups should remain unchanged.

API: {py:class}`pdl.Group`, {py:meth}`pdl.Entity.copy`, {py:meth}`pdl.Group.child`.


---

[Part contents](index.md)
