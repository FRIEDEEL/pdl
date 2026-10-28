# 6.2 How TeX becomes a drawing

A formula has to be typeset before pdl can know its width, height, and baseline.
That work happens even if your final output is SVG.

## Use a shared environment

```{literalinclude} ../../../../examples/tutorial/advanced/tex_pipeline.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![A formula inside an automatically measured node](../../../../examples/output/tutorial/advanced/tex_pipeline.svg)

[Complete runnable example](../../../../examples/tutorial/advanced/tex_pipeline.py)

`TeXConfig` supplies packages and preamble commands. The formula uses the
custom `\energy` command, while the Node uses the measured formula box to
choose its size. The same configuration is used for measurement and native output.

## Measurement and SVG output

pdl asks XeLaTeX to typeset the fragment and report its box dimensions. dvisvgm
converts the fragment to SVG outlines, retaining its baseline information.
The SVG adapter places that fragment in the drawing. Unlike ordinary SVG Text,
the formula does not rely on the browser to find the original font.

Measurements are cached using the source, tool versions, configuration, and
explicit dependency file contents. List changing external files in
`TeXConfig.dependencies`; after external package changes, change `cache_salt`
when cache invalidation is needed. The cache does not discover every external
TeX dependency automatically.

## Native TikZ output

The TikZ adapter keeps the LaTeX source and adds the shared preamble to the
document. Compiling the resulting document typesets it again. Slight differences
between independently measured fragments and final typesetting can remain.
One native TikZ document must use a shared compatible TeXConfig.

The complete example saves an SVG, `.tex` source, and compiled PDF. XeLaTeX,
dvisvgm, standalone, and the configured packages must be installed. Importing
pdl or constructing TeX does not run these tools; measuring/rendering does.
Saving TikZ source with `tikz_mode="tex"` avoids final PDF compilation, but
it does not eliminate the tools needed for fragment measurement.

## Try it

Change the preamble command to define a different symbol, and rerun. The formula
and its surrounding node update. Use the [output guide](../../../tikz-output.md)
for compilation modes, intermediate files, and embedding an exported picture.

API: {py:class}`pdl.TeXConfig`, {py:class}`pdl.TeX`, {py:meth}`pdl.Canvas.save`.


---

[Part contents](index.md)
