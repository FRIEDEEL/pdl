# 3.3 Operate on overlapping selections

Gather is an explicit collection of Entity identities, with no ownership or inherited paint. It can select a Group as one target or select individual members directly. Overlapping Group/member transform selections are applied once.

`Gather.set_style` calls set_style on exactly the selected objects. To change member styles together, collect those members explicitly. Combine selections with their members or union/intersection/difference operations; nested Gather objects are not Entity members.

## Runnable examples and output

```{literalinclude} ../../../../examples/tutorial/layout/gathers.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![17. Operate on overlapping selections](../../../../examples/output/tutorial/layout/gathers.svg)

Full source: [gathers.py](../../../../examples/tutorial/layout/gathers.py).

---

[Part contents](index.md)
