# 3.3 Operate on overlapping selections

Gather collects existing operation units without changing their Group or Layer
membership. It has no coordinate frame or inherited style. Different Gathers
may share an instance.

```{literalinclude} ../../../../examples/tutorial/layout/gathers.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![17. Operate on overlapping selections](../../../../examples/output/tutorial/layout/gathers.svg)

[Complete runnable example](../../../../examples/tutorial/layout/gathers.py)

The lower row is the initial capture. `combined` contains the component only
once even though both selections include it. Translating it moves both units
once; rotating `second` then affects only the component, in command order.

Adding another Gather copies its current members into the flat identity set;
subsequent additions/removals do not follow the original selection. Use `add`,
`remove`, `union`, `intersection`, and `difference` for membership operations.
Gather itself cannot be submitted to `canvas.draw`.

Selecting a grouped child promotes it to the outermost Group with a UserWarning.
Targets are normalized again before each command, so grouping after selection
cannot transform a child twice. Use `members` to inspect the actual targets.
Recreate selections targeting a dismissed Group.

Try adding `marker` to `second`; it will receive both commands exactly once each.

[Compare Group, Layer, and Gather](05-comparison.md)

---

[Part contents](index.md)
