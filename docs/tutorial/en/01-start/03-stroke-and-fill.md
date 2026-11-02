# 1.3 Outlines and fills

Style is an immutable, complete paint description. `stroke=None` disables the outline and `fill=None` disables the interior. Line width uses final output millimeters; colors have RGB channels in [0, 1]. Native text and TeX use solid fill paint with no stroke.

Store paint on the Entity with a factory's `style=` argument or `set_style`. A `Canvas.draw(entity, style)` override is captured for that submission and leaves the source instance unchanged. An unset Entity style remains None; effective defaults are resolved when needed.

## Runnable examples and output

```{literalinclude} ../../../../examples/tutorial/basics/stroke.py
:language: python
:start-at: from pdl import
:end-before: output =
```

![stroke](../../../../examples/output/tutorial/basics/stroke.svg)

```{literalinclude} ../../../../examples/tutorial/basics/fill.py
:language: python
:start-at: from pdl import
:end-before: output =
```

![fill](../../../../examples/output/tutorial/basics/fill.svg)

```{literalinclude} ../../../../examples/tutorial/basics/fill_only.py
:language: python
:start-at: from pdl import
:end-before: output =
```

![fill only](../../../../examples/output/tutorial/basics/fill_only.svg)

```{literalinclude} ../../../../examples/tutorial/basics/colored_shapes.py
:language: python
:start-at: from pdl import
:end-before: output =
```

![colored shapes](../../../../examples/output/tutorial/basics/colored_shapes.svg)

Full source: [stroke.py](../../../../examples/tutorial/basics/stroke.py), [fill.py](../../../../examples/tutorial/basics/fill.py), [fill_only.py](../../../../examples/tutorial/basics/fill_only.py), [colored_shapes.py](../../../../examples/tutorial/basics/colored_shapes.py).

---

[Part contents](index.md)
