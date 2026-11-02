# 1.5 Words and formulas

Text is literal Unicode; TeX interprets LaTeX source. Their reference position is a baseline point in millimeters, and size uses TeX points (1/72.27 inch). Fonts and TeX configuration participate in measurement.

Queries measure lazily, and Canvas submission captures the selected fonts/configuration and layout. Translation and rotation retain native descriptions. Positive uniform scaling preserves native Text, while TeX scaling transforms measured outlines so fixed dimensions scale correctly. Stretch, shear, and reflection also irreversibly replace text with paths. Unsupported rich/colored TeX outlines raise an error. TeX measurement requires XeLaTeX and dvisvgm.

## Runnable examples and output

```{literalinclude} ../../../../examples/tutorial/text/labels.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![Two labels with their baselines](../../../../examples/output/tutorial/text/labels.svg)

```{literalinclude} ../../../../examples/tutorial/text/formula.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![A formula typeset by LaTeX](../../../../examples/output/tutorial/text/formula.svg)

Full source: [labels.py](../../../../examples/tutorial/text/labels.py), [formula.py](../../../../examples/tutorial/text/formula.py).

---

[Part contents](index.md)
