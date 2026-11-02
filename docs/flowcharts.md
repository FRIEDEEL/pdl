# Editable growing flowcharts

FlowNode represents a process, Decision a diamond, and Terminal a circular end.
right/left/above/below place a fresh child and return it. The default gap is
12 mm between boundaries. Label layout participates in expansion; later label
edits recompute future captures, and moving a parent moves grown descendants.

connect(existing) links an existing node without moving it and returns an
editable FlowEdge. Ports, labels, via points, and style can be changed. Orthogonal
routes use cardinal-port elbows; route="straight" draws a direct segment, and
explicit via points override elbow generation. There is no obstacle avoidance.

Submitting a root captures its reachable outgoing graph, including merges and
feedback cycles. Edges paint before nodes. Expansion uses the Canvas typography
policy and fixes the result; later source edits leave previous submissions alone.
The result uses ordinary Entity/Group objects for copies and transforms. A
standalone Connection evaluates endpoints once and has no live node binding.

```{literalinclude} ../examples/flowcharts/growing.py
:language: python
:start-at: start =
:end-before: canvas =
```

![Growing flowchart](../examples/output/flowcharts/growing.svg)

[API](api/flowcharts.md)
