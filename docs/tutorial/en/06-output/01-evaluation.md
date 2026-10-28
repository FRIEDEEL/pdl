# 6.1 From your objects to an image

The earlier chapters describe what to draw. Now let's look at when those
descriptions turn into measured geometry and output text.

## Three steps

1. **Author:** create shapes, labels, placements, and references. `draw` records
   the state you add without measuring fonts.
2. **Resolve:** evaluate positions and typography with the canvas's current
   settings, then apply the viewport mapping.
3. **Export:** an adapter writes SVG or TikZ. It uses native objects where
   supported and decomposes other objects as needed.

Resolved data does not mean everything becomes a Path. Rectangles, circles,
measured text, and nodes can retain their native types. For example, TikZ can
output a native node under translation/rotation; more general affine placement
may require decomposition. Output is not guaranteed pixel-identical across adapters.

## Keep a fixed result

```{literalinclude} ../../../../examples/tutorial/advanced/resolved.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![Original label and later moved label](../../../../examples/output/tutorial/advanced/resolved.svg)

[Complete runnable example](../../../../examples/tutorial/advanced/resolved.py)

`canvas.resolve(label)` measures the original label before we move the Entity.
The main canvas shows both recorded states. The `copy` canvas receives only
the fixed original result:

![Fixed original label](../../../../examples/output/tutorial/advanced/resolved-copy.svg)

The snapshot has fixed positions and typography metrics. It still needs font
or TeX resources for native text output; it is not an embedded bitmap or a
self-contained portable font package. Drawing it on another canvas applies
that destination's mapping to the fixed geometry.

A regular render reevaluates dependencies each time. A reference captures an
authoring description; a resolved result fixes its measurements too. This is
why changing fonts can affect a regular reference but not its resolved metrics.

## Choose output

`canvas.render("svg")` returns XML text. `canvas.render("tikz")` returns TeX
source; `standalone=False` requests an embeddable TikZ picture. `save` writes
those sources and can compile a TikZ PDF. Keep source suffix and backend
consistent: a filename extension does not choose the adapter.

## Try it

Move the label farther before the second draw call. The copied snapshot stays
at its original position. Querying an object's dependencies does not draw them,
and dependency evaluation never rearranges paint order.

API: {py:meth}`pdl.Canvas.resolve`, {py:class}`pdl.ResolvedGraphic`,
{py:meth}`pdl.Canvas.render`. See the [TikZ output guide](../../../tikz-output.md).


---

[Part contents](index.md)
