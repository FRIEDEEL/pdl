# API reference — pdl

The reference follows the packages and modules under `src/pdl/`. Choose a package below, then open a module for its classes, functions, signatures, and source docstrings.

Lengths and line widths use millimeters; text and TeX sizes use TeX points. Entity edits take effect immediately, position queries return fixed values, and Canvas captures submissions independently of subsequent edits.

The reference is maintained in English. [Start with the tutorial](../tutorial/en/index.md) for guided examples.

The root package exposes everyday drawing factories, Entity, Group, Gather,
Canvas, Style, and Color. Use the owning subpackages for pure geometry,
explicit transforms, advanced paint, Canvas helpers, and extensions.

Source: `src/pdl/__init__.py`.

```{eval-rst}
.. automodule:: pdl
```

## Packages and modules

```{toctree}
:maxdepth: 1

author/index
backends/index
canvas/index
extensions/index
```

## Re-exported names

These imports link to their defining modules. Full member documentation is kept at the definition rather than repeated here.

| Import | Defined in |
| --- | --- |
| `pdl.Canvas` | {py:obj}`pdl.canvas.canvas.Canvas` |
| `pdl.Color` | {py:obj}`pdl.author.style.color.Color` |
| `pdl.Entity` | {py:obj}`pdl.author.entity.base.Entity` |
| `pdl.Gather` | {py:obj}`pdl.author.entity.gather.Gather` |
| `pdl.Group` | {py:obj}`pdl.author.entity.group.Group` |
| `pdl.Style` | {py:obj}`pdl.author.style.style.Style` |
| `pdl.arc` | {py:obj}`pdl.author.entity.factories.arc` |
| `pdl.circle` | {py:obj}`pdl.author.entity.factories.circle` |
| `pdl.frame_axes` | {py:obj}`pdl.author.entity.factories.frame_axes` |
| `pdl.image` | {py:obj}`pdl.author.entity.factories.image` |
| `pdl.line` | {py:obj}`pdl.author.entity.factories.line` |
| `pdl.path` | {py:obj}`pdl.author.entity.factories.path` |
| `pdl.polygon` | {py:obj}`pdl.author.entity.factories.polygon` |
| `pdl.polyline` | {py:obj}`pdl.author.entity.factories.polyline` |
| `pdl.rectangle` | {py:obj}`pdl.author.entity.factories.rectangle` |
| `pdl.tex` | {py:obj}`pdl.author.entity.factories.tex` |
| `pdl.text` | {py:obj}`pdl.author.entity.factories.text` |
