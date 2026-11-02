# pdl — Python Drawing Library

pdl builds static vector drawings from Python objects: 2D shapes and paths,
Unicode text and TeX, reusable components, diagram connections, and projected
3D solids. SVG and TikZ/PDF share the same Author domain. Python 3.12+ is required.

[中文说明](README_zh.md) · [Tutorial](docs/tutorial/en/index.md) ·
[API reference](docs/api/index.md) · [Architecture](docs/architecture.md)

## Draw and save

Run from the repository after selecting Python with pyenv and installing with
`uv sync`. The SVG needs an installed font. TeX measurement uses XeLaTeX and
dvisvgm; native-font PDF output uses XeLaTeX and the required LaTeX packages.

```python
from pdl import Canvas, Color, Group, Style, circle, line, text

disk = circle((20, 25), 10, style=Style(fill=Color(0.7, 0.85, 1)))
connector = line((35, 10), (70, 35), style=Style(line_width=0.5))
label = text("A reusable component", position=(12, 45), size=11)
component = Group(disk, connector, label)
canvas = Canvas(80, 55).add(component)
canvas.save("drawing.svg")
canvas.save("drawing.tex", backend="tikz", tikz_mode="pdf")
```

`circle`, `rectangle`, `text`, and the other drawing factories return Entity objects.
Pure descriptions such as `Path` live in `pdl.author.geometry`. Entity attaches
style and drawing operations to a description. Canvas.add/draw captures the current
state, so later edits require another submission.

## Explicit capabilities

The root exports drawing factories, Entity, Group, Gather, Canvas, Style, and
Color. Import other capabilities from the package that owns them:

```python
from pdl.author.geometry import Path, Point
from pdl.author.style import Font, LinearGradient
from pdl.author.transform import Rotation
from pdl.canvas import Layer, Query
from pdl.extensions.diagram import Node
from pdl.extensions.spatial import Scene3D, PerspectiveCamera
```

Pure geometry is introduced when constructing descriptions explicitly. The 3D
and diagram packages have independent public entrypoints and load on request.

## Author behavior

- Geometry stores current coordinates and shape parameters. Entity directly holds
  geometry and optional Style, with reference/center/anchor queries.
- Entity methods edit immediately and return the same object. A stretched Circle
  can become Path geometry while retaining Entity identity. No accumulated object
  transform or implicit local frame is stored.
- Rotation/scaling defaults to the reference point: circle center, rectangle
  origin, path's first Move, text baseline, or explicit Group reference. Use origin
  for another pivot, or set_reference to choose future default pivots.
- Line width stays fixed by default. Uniform rescale can explicitly include it;
  nonuniform scaling has no line-width option.
- Entity.style None stays unset. Effective paint falls back through explicitly
  styled Groups and then defaults. Group.set_style changes the Group alone;
  Gather(*group.members).set_style explicitly changes its members.
- Group is an Entity with one-parent ownership. Gather is an overlapping identity
  selection. Layer belongs to Canvas and determines coverage order.
- Positions use world millimeters, x right and y up. An explicit Frame supplies
  numerical coordinate conversion; frame_axes creates drawable axes.
- Text/TeX measure when needed; sizes use TeX points. Text retains native form
  under orientation-preserving similarities. TeX translation/rotation retain
  source; scaling outlines the measured artwork. Other deformations also lower
  text to paths irreversibly; unsupported rich TeX outlines raise an error.
- Canvas snapshots isolate geometry, paint, typography, and ordering from future
  source edits. Backends encode captured Entities without a second scene model.

To retain an editable version, call copy. Directly sharing mutable geometry is
possible; direct geometry edits are shared, while Entity transforms replace only
the target's geometry. See the [copy/capture lesson](docs/tutorial/en/02-shapes/03-copy-and-capture.md).

## Components and 3D

Write parameterized Python functions or Entity/Group subclasses for a local
component library. Combine shapes, query current anchors, and submit the resulting
Group. A position query returns fixed numbers; later source edits do not create
live constraints or automatically redraw dependent connections.

Scene3D.project produces a 2D ProjectedScene Group. Orthographic/perspective
cameras, indexed polyhedra, plane artwork, smooth cylindrical surfaces, shading,
and BSP visibility are available. Curved/artwork scenes use documented centroid
ordering limits. Independently projected components follow ordinary Canvas order.

Examples remain organized under [examples](examples): geometry, composition,
text, diagrams, coordinates, spatial, and the seven-part tutorial. Outputs mirror
source paths under examples/output and remain outside Git.

## Build and validate

```sh
uv run ruff check .
uv run ruff format --check .
uv run pyright
uv run pytest
uv run python -m examples.tutorial.render_all
uv run python -m examples.tools.render_all --tikz-mode pdf
uv run --group docs sphinx-build -W --keep-going -b html docs docs/_build/html
uv build
```

Open docs/_build/html/index.html. The documentation build generates actual
illustrations from runnable sources. See [building](docs/building.md) for tools
and [migration](CHANGELOG.md) for incompatible API changes. Native font rendering
can differ across SVG viewers and LaTeX. Nonlinear/mesh transforms, automatic
obstacle routing, isolated group transparency, and solid booleans are future work.
