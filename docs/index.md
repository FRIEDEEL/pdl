# Draw with pdl

| Build information | Value |
| --- | --- |
| Version | {{ build_version }} |
| Commit | {{ build_commit }} |
| Branch | {{ build_branch }} |

pdl is a Python library for static vector drawings. Start with a small labeled
box, learn shapes and styles, then build connected and reusable components.
Export SVG or TikZ without changing the objects that describe your drawing.
Drawing factories return thin Entities containing current geometry and optional
Style. Edits take effect immediately; Canvas captures independent submissions.

## Start drawing

- [Tutorial](tutorial/en/index.md)
- [API reference](api/index.md): exact signatures, defaults, units, and behavior.

```{toctree}
:maxdepth: 3
:caption: Tutorials

tutorial/en/index
```

```{toctree}
:maxdepth: 2
:caption: Reference and guides

api/index
architecture
coordinates
flowcharts
spatial
tikz-output
```

## Scope

The current library supports shapes, paths, ordinary text, TeX, nodes,
connectors, groups, affine transforms, explicit frames, and viewport fitting.
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
