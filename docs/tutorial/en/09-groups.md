# 9. Reuse a group of objects

Our small component is a rectangular body with a circular port. We want to
place it twice and rotate one copy without recalculating its parts.

```{literalinclude} ../../../examples/tutorial/layout/groups.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![One component reused in two placements](../../../examples/output/tutorial/layout/groups.svg)

[Complete runnable example](../../../examples/tutorial/layout/groups.py)

`Group` collects ordered `Drawing` records. Each Drawing pairs an object
with optional paint and placement. Inside the component, the body is centered
on `(0, 0)` and the port is at `(11, 0)`.

`first` and `second` reuse the same component definition, with different
placements. The second rotates local coordinates before translating them to
`(60, 20)`. Both body and port move together, retaining their relative spacing.
The original component is unchanged.

To get a specific placed part, use `second.child(1)` for the port. Its anchors
include the second instance's accumulated transform. A group anchor instead
refers to the group's axis-aligned bounds, which is often the wrong place to
attach a wire to a particular port.

A child with an explicit style uses that style. Otherwise it inherits its
parent's style as a whole; styles do not merge field by field.

## Try it

Add a third Drawing of the same component with another transform. Then change
the port's radius in the component definition and rerun: all instances use
the updated definition. A Group describes an assembly, while paint order still
comes from its children and the canvas draw calls. It is not a Layer API.

API: {py:class}`pdl.Group`, {py:class}`pdl.Drawing`, {py:meth}`pdl.Drawing.child`.

---

[Previous: Anchors and connections](08-anchors.md) · [Next: Custom paths and curves](10-paths.md)
