# Growing flowcharts

Use `FlowNode` for a process, `Decision` for a diamond, and `Terminal` for a
circular start/end. These editable components are separate from the immutable
low-level `Node` API. No parser or external layout engine is involved.

```{literalinclude} ../examples/flowcharts/growing.py
:language: python
:start-at: start =
:end-before: canvas =
```

![Growing flowchart](../examples/output/flowcharts/growing.svg)

`a.right(b)` places a fresh child and connects it, returning **b** for further
growth. `left`, `above`, and `below` work the same way. The default gap is 12 mm
between shape boundaries; labels are measured with the eventual renderer fonts.
A child's initial position acts as an additional offset from its grown position.
Changing label content or dimensions recomputes spacing. Translating a parent
also moves its grown descendants; unrelated branches retain their placement.

Use `connect(existing)` for merges and feedback, without moving the target.
It returns an editable `FlowEdge`: set `start`/`end` ports, `via` waypoints,
`label`, and `style`. Cardinal ports default to horizontal/vertical elbows computed from their current
positions. Set `route="straight"` for a direct segment. Explicit `via` waypoints
override this routing. There is no obstacle avoidance. Prefer cardinal ports on diamond nodes.
Edge labels sit beside the route midpoint; dense diagrams can still overlap.

Draw the root once to include the outgoing graph, including cycles, and any
placement ancestors. Connections render before nodes. `Canvas.draw` captures
node and edge state without measuring fonts. Later edits affect future draws,
not previous records. Treat a captured graph as one composite for subsequent
Entity or Group transforms; live flow nodes are edited before capturing.

Run `uv run python examples/flowcharts/growing.py` for SVG, TikZ, and PDF output
under `examples/output/flowcharts/` (PDF requires XeLaTeX). Inspect both the source
and output when evaluating the API. [中文说明](flowcharts_zh.md).
