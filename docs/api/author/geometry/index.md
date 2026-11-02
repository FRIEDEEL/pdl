# pdl.author.geometry

`Geometry` is the nominal base for descriptions accepted by Entity and backend
geometry dispatch. It requires no shared state or operations. Inherit it for
custom descriptions; implement optional capabilities such as `to_path()` only
where meaningful. Membership alone does not guarantee rendering support.

`text` and `tex` factories create Entities around dedicated native descriptions.
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

Source: `src/pdl/author/geometry/__init__.py`.

```{eval-rst}
.. automodule:: pdl.author.geometry
```

## Packages and modules

```{toctree}
:maxdepth: 1

base
bounds
commands
frame
image
path
point
protocols
queries
shapes
tex
tex_svg
text
typography
```

## Re-exported names

These imports link to their defining modules. Full member documentation is kept at the definition rather than repeated here.

| Import | Defined in |
| --- | --- |
| `pdl.author.geometry.Arc` | {py:obj}`pdl.author.geometry.shapes.Arc` |
| `pdl.author.geometry.Bounds` | {py:obj}`pdl.author.geometry.bounds.Bounds` |
| `pdl.author.geometry.Circle` | {py:obj}`pdl.author.geometry.shapes.Circle` |
| `pdl.author.geometry.CoordinateSystem` | {py:obj}`pdl.author.geometry.frame.CoordinateSystem` |
| `pdl.author.geometry.Frame` | {py:obj}`pdl.author.geometry.frame.Frame` |
| `pdl.author.geometry.Geometry` | {py:obj}`pdl.author.geometry.base.Geometry` |
| `pdl.author.geometry.Image` | {py:obj}`pdl.author.geometry.image.Image` |
| `pdl.author.geometry.Line` | {py:obj}`pdl.author.geometry.shapes.Line` |
| `pdl.author.geometry.Path` | {py:obj}`pdl.author.geometry.path.Path` |
| `pdl.author.geometry.Point` | {py:obj}`pdl.author.geometry.point.Point` |
| `pdl.author.geometry.Polygon` | {py:obj}`pdl.author.geometry.shapes.Polygon` |
| `pdl.author.geometry.Polyline` | {py:obj}`pdl.author.geometry.shapes.Polyline` |
| `pdl.author.geometry.Position` | {py:obj}`pdl.author.geometry.point.Position` |
| `pdl.author.geometry.Rectangle` | {py:obj}`pdl.author.geometry.shapes.Rectangle` |
| `pdl.author.geometry.SpacePoint` | {py:obj}`pdl.author.geometry.frame.SpacePoint` |
| `pdl.author.geometry.SpaceVector` | {py:obj}`pdl.author.geometry.frame.SpaceVector` |
| `pdl.author.geometry.TeX` | {py:obj}`pdl.author.geometry.tex.TeX` |
| `pdl.author.geometry.Text` | {py:obj}`pdl.author.geometry.text.Text` |
| `pdl.author.geometry.Vector` | {py:obj}`pdl.author.geometry.point.Vector` |
| `pdl.author.geometry.WORLD` | {py:obj}`pdl.author.geometry.frame.WORLD` |
