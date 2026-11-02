# 4.3 Choose what fits on the page

Clip keeps a fixed viewport; fit uniformly scales and centers submitted content inside fixed dimensions; auto_size derives dimensions and translates content with padding. Logical geometry/layout bounds and conservative stroke margins determine fitting.

Final viewport operations use captured state and preserve line widths in output millimeters. Padding must leave a fitting area. Empty auto-size output remains a valid small page.

## Runnable examples and output

```{literalinclude} ../../../../examples/tutorial/advanced/viewport_clip.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![Fixed viewport clips the circle](../../../../examples/output/tutorial/advanced/viewport_clip.svg)

```{literalinclude} ../../../../examples/tutorial/advanced/viewport_fit.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![Fit shows all content in the fixed viewport](../../../../examples/output/tutorial/advanced/viewport_fit.svg)

```{literalinclude} ../../../../examples/tutorial/advanced/viewport_auto_size.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![Auto-size preserves scale and changes canvas dimensions](../../../../examples/output/tutorial/advanced/viewport_auto_size.svg)

Full source: [viewport_clip.py](../../../../examples/tutorial/advanced/viewport_clip.py), [viewport_fit.py](../../../../examples/tutorial/advanced/viewport_fit.py), [viewport_auto_size.py](../../../../examples/tutorial/advanced/viewport_auto_size.py).

---

[Part contents](index.md)
