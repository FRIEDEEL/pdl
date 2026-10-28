# Draw with pdl

pdl is a Python library for static vector drawings. Start with a small labeled
box, learn shapes and styles, then build connected and reusable components.
Export SVG or TikZ without changing the objects that describe your drawing.

## Start drawing

- [English tutorial](tutorial/en/index.md)
- [中文教程](tutorial/zh/index.md)
- [API reference](api/index.md): exact signatures, defaults, units, and behavior.

```{toctree}
:maxdepth: 3
:caption: Tutorials

tutorial/en/index
tutorial/zh/index
```

```{toctree}
:maxdepth: 2
:caption: Reference and guides

api/index
coordinates
coordinates_zh
flowcharts
flowcharts_zh
spatial
spatial_zh
tikz-output
tikz-output_zh
```

## Scope

The current library supports shapes, paths, ordinary text, TeX, nodes,
connectors, groups, affine transforms, authoring frames, and viewport fitting.
Editable groups, flat overlapping Gathers, ordered layers, PNG/JPEG images,
per-leaf opacity, and linear/radial gradient fills are supported. Layer groups,
isolated compositing, general automatic graph layout, and automatic routing are not implemented.
Growing flowcharts support boundary-spaced directional placement and editable connections. Public interfaces remain provisional.

[Build and maintain these docs](building.md).

Teaching references: [Manim Community Quickstart](https://docs.manim.community/en/stable/tutorials/quickstart.html)
and the [PGF/TikZ manual](https://tikz.dev/). Their APIs differ from pdl;
only the pdl interfaces documented here are supported.

```{toctree}
:hidden:

building
```
