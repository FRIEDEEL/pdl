# 15. Multiple subpaths and holes

One Path can contain several separate outlines. Which enclosed parts get
filled depends on its fill rule. Let's combine two concentric circles.

```{literalinclude} ../../../examples/tutorial/advanced/fill_rules.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![Nonzero fill on the left, evenodd on the right](../../../examples/output/tutorial/advanced/fill_rules.svg)

[Complete runnable example](../../../examples/tutorial/advanced/fill_rules.py)

`extend` appends each circle as its own subpath, without a connecting line.
Both circles have the same winding direction. On the left, the default
`nonzero` rule fills the center too. On the right, `evenodd` leaves a hole:
crossing two boundaries takes you outside again.

The difference affects fill only. Both circular outlines are still stroked.
The circles become cubic path approximations when converted by `extend`;
they are no longer separate native Circle objects in this Path.

With the nonzero rule, reversing the inner contour can also produce a hole.
The important distinction is the direction and number of boundary crossings,
not which subpath was created last. This is separate from paint order between
two independent draw calls.

## Try it

Set both styles to `fill_rule="evenodd"` and confirm that both sides have holes.
Then reduce the inner radius. Both examples use the same captured path with
a different placement and style.

API: {py:meth}`pdl.Path.extend`, {py:class}`pdl.Style`.

---

[Previous: TeX rendering](14-tex-rendering.md)

[Next / 下一章: Editable groups](16-editable-groups.md)
