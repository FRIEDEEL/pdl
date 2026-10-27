# 5. Words and formulas

A Node includes a label and an enclosing shape. Use {py:class}`pdl.Text` when
you want just the words, without a box.

## Place ordinary text

```{literalinclude} ../../../examples/tutorial/text/labels.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![Two labels with their baselines](../../../examples/output/tutorial/text/labels.svg)

[Complete runnable example](../../../examples/tutorial/text/labels.py)

The two gray lines mark the **baselines**. Unlike a Node's position, a Text
position is not its center: with the default left alignment, it marks the left
baseline reference. Letters sit mostly above it; descenders can extend below.
Remove the optional guide section when you no longer need it.

`size` is in TeX points, not millimeters. One point is 1/72.27 inch. The labels
use the default system font; font coverage and appearance depend on what is
installed. `Text` treats its content literally, so `$x^2$` is printed as text.
A newline starts a new line; automatic paragraph wrapping is not provided.

When supplying a text style, use `Style(stroke=None, fill=...)`. Native text
currently supports fill paint only. With no style supplied, it is black.

## Typeset a formula

Before running this example, install XeLaTeX and dvisvgm, with the LaTeX
`standalone` class and `amsmath` package. A suitable TeX Live installation
provides them. Check that the executables are visible:

```sh
xelatex --version
dvisvgm --version
```

```{literalinclude} ../../../examples/tutorial/text/formula.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![A formula typeset by LaTeX](../../../examples/output/tutorial/text/formula.svg)

[Complete runnable example](../../../examples/tutorial/text/formula.py)

`TeX` interprets LaTeX. The dollar signs select math mode. The Python `r`
prefix keeps backslashes in expressions such as `r"$\frac{a}{b}$"` intact.
Its position is also a left baseline reference, and its size is in TeX points.

The complete example saves both an SVG and a native TikZ PDF. You can continue
with non-TeX chapters before installing these tools; ordinary Text does not
need them for SVG output.

## Try it

Change the formula to `r"$a^2 + b^2 = c^2$"`, then increase the canvas width if
needed. Change the ordinary label to `"First line\nSecond line"` to try an
explicit line break. [TeX rendering](14-tex-rendering.md) explains the tools later.

API: {py:class}`pdl.Text`, {py:class}`pdl.TeX`, {py:class}`pdl.FontStack`.

---

[Previous: Drawing order](04-drawing-order.md) · [Next: Move, rotate, and scale](06-transforms.md)
