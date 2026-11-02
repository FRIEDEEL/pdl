# Typography and external-tool configuration

Text and TeX factories create Entities around dedicated native descriptions.
Position is a baseline point, size is in TeX points, and rotation is the current
orientation. Measurement is lazy. Canvas fixes font candidates, TeX environment,
and measured layout on submission. Captured Entities remain ordinary editable
objects; explicitly editing captured content refreshes its layout.

Text retains native form under translation, rotation, and orientation-preserving
uniform scale. TeX retains native source under translation/rotation, but scaling
outlines the measured artwork: changing font size cannot scale absolute TeX
dimensions. Other affine deformations also lower text to paths. Conversion loses
layout whitespace; subsequent bounds describe the resulting contours. Rich/colored
TeX SVG can remain embedded; unsupported outline conversion raises an error,
including scaling requested by Canvas fit. Native
fonts depend on installed/viewer fonts and do not promise identical rasterization
between SVG and LaTeX. Ordinary Text supports horizontal left-to-right labels,
with explicit newlines and no automatic wrapping; missing glyphs and unsupported
bidirectional content are reported explicitly.

## Font

```{eval-rst}
.. autoclass:: pdl.Font
   :members:
   :member-order: bysource
```

## FontStack

```{eval-rst}
.. autoclass:: pdl.FontStack
   :members:
   :member-order: bysource
```

## TeXConfig

```{eval-rst}
.. autoclass:: pdl.TeXConfig
   :members:
   :member-order: bysource
```

## RendererConfig

```{eval-rst}
.. autoclass:: pdl.RendererConfig
   :members:
   :member-order: bysource
```

## Text drawing factory

```{eval-rst}
.. autofunction:: pdl.Text
```

### Native Text description

```{eval-rst}
.. autoclass:: pdl.author.geometry.text.Text
   :members:
   :member-order: bysource
```

## TeX drawing factory

```{eval-rst}
.. autofunction:: pdl.TeX
```

### Native TeX description

```{eval-rst}
.. autoclass:: pdl.author.geometry.tex.TeX
   :members:
   :member-order: bysource
```
