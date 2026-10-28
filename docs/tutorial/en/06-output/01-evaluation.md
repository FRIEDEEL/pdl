# 6.1 From your objects to an image

Author objects are the only drawing model. Anchor and placement operations
compute numerical results when called. Text queries use the current font or TeX
measurement environment; they do not wait for final rendering.

`canvas.draw(object)` captures the current state and fixes typography using that
canvas's settings. Later edits and per-render font overrides do not relayout old
records. Draw again to submit a new state. The backend receives ordinary captured
shapes, text, images and groups, not an independent resolved scene.

## Keep a fixed result

```{literalinclude} ../../../../examples/tutorial/advanced/snapshots.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![Original label and later moved label](../../../../examples/output/tutorial/advanced/snapshots.svg)

[Complete runnable example](../../../../examples/tutorial/advanced/snapshots.py)

`canvas.snapshot(label)` returns an ordinary Drawing in authoring coordinates,
with fixed layout, without submitting it. The second canvas draws that same
captured description:

![Fixed original label](../../../../examples/output/tutorial/advanced/snapshots-copy.svg)

Native text still needs fonts or TeX resources. SVG viewers and native LaTeX can
shape glyphs differently; fixed layout does not promise pixel-identical output.

## Choose output

`canvas.render("svg")` returns XML; `canvas.render("tikz")` returns TeX source.
`save` writes output and optionally compiles a TikZ PDF. Canvas fitting and
resource collection operate on the final submitted paint list. Paint order is
independent of the order in which anchors were calculated.

API: {py:meth}`pdl.Canvas.snapshot`, {py:meth}`pdl.Canvas.render`.
See the [TikZ output guide](../../../tikz-output.md).

---

[Part contents](index.md)
