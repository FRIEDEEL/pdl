# 3.2 Edit and dissolve groups

Edit a Group with add, remove, and dismiss. Ownership changes preserve current world geometry. Dismiss returns detached members; their paint is resolved from their remaining explicit style and new ownership.

Changing a member directly changes that member. A Group transformation edits its existing family, and a failed conversion leaves the family unchanged. Submission captures the current result independently.

## Runnable examples and output

```{literalinclude} ../../../../examples/tutorial/layout/editable_groups.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![16. Edit and dissolve groups](../../../../examples/output/tutorial/layout/editable_groups.svg)

Full source: [editable_groups.py](../../../../examples/tutorial/layout/editable_groups.py).

---

[Part contents](index.md)
