# pdl — Python Drawing Library

A typed Python library for static vector drawings: geometry, paths, text,
LaTeX formulas, connected nodes, reusable groups, and affine coordinate systems,
with SVG and TikZ output. Editable Groups, overlapping Gather selections,
ordered layers, PNG/JPEG embedding, opacity, and linear/radial fills are included. Python 3.12 or later is required.

[中文说明](README_zh.md) · [English tutorial](docs/tutorial/en/index.md) ·
[中文教程](docs/tutorial/zh/index.md) · [API reference](docs/api/index.md)

## Read the documentation

Build the local documentation site from the repository root:

```sh
uv sync --group docs
uv run --group docs sphinx-build -W --keep-going -b html docs docs/_build/html
```

Open `docs/_build/html/index.html` in a browser. The build generates all tutorial
images and includes code directly from runnable examples. The full manual
requires a usable system sans-serif font, XeLaTeX, dvisvgm, and the LaTeX
standalone, amsmath, and TikZ packages. See the [build guide](docs/building.md).
The site is local; no public hosting is configured.

## A small drawing

```python
from pdl import Canvas, Circle, Color, Path, Style

canvas = Canvas(80, 50)
canvas.draw(Circle((20, 25), 10), Style(fill=Color(0.7, 0.85, 1)))
curve = Path().move_to((35, 10)).cubic_to((40, 45), (65, 45), (70, 10))
canvas.draw(curve, Style(line_width=0.5))
canvas.save("drawing.svg", backend="svg")
canvas.save("drawing.tex", backend="tikz")
```

## Coordinate and painting conventions

- Coordinates and line widths are millimeters. The fixed viewport starts at
  `(0, 0)` in the bottom-left; x points right and y points up. Outside content
  is clipped. Angles are degrees, positive counterclockwise.
- `Point` is a coordinate value, not a drawable. Coordinate pairs are also accepted.
- `Line`, `Polyline`, `Circle`, `Rectangle`, `Polygon`, `Arc` and `Path` describe
  geometry. `Style` describes paint; `Canvas.draw` appends a drawing.
- The default style is black stroke, width 1 mm, no fill, butt caps and miter
  joins (miter limit 10). Colors use RGB channels between 0 and 1.
- Layers paint bottom-to-top; objects within a layer render in insertion order. Native shape identity is retained until
  backend dispatch; unsupported geometry falls back through `to_path()`.
- Paths are mutable builders. A draw call captures their current commands;
  later edits require another draw call. `path.to_path()` makes an independent copy.
- Paths support absolute `move_to`, `line_to`, `quadratic_to`, `cubic_to`,
  `arc` and `close`. Quadratic curves have one control point, cubic curves two.
- `close()` closes the current subpath and returns the current point to its
  start. Fill implicitly closes each open subpath without closing its stroke.
  Fill rules are `nonzero` (default) and `evenodd`.
- Zero-width strokes are suppressed in both backends. Invalid geometry and
  paint values raise ordinary Python exceptions. No custom exception hierarchy.

## Arcs

`Arc(center, radius_x, radius_y, start_angle, sweep_angle, rotation=0)` is
canonical. Radii must be positive; the signed sweep is at most 360 degrees.
Two constructors offer familiar parameterizations independently of output:

```python
from pdl import Arc

arc = Arc.from_tikz((10, 20), radius=8, start_angle=90, end_angle=270)
arc = Arc.from_svg(
    (10, 20),
    (30, 25),
    radius_x=15,
    radius_y=8,
    rotation=20,
    large_arc=False,
    sweep=True,
)
```

`from_tikz` starts at the supplied point; `radius_y` optionally gives an ellipse.
`from_svg` uses SVG endpoint conversion and radius correction, but coordinates
remain Cartesian: `sweep=True` follows increasing angle, visually counterclockwise.
Negative SVG input radii are made positive; zero radii return a `Line`;
coincident endpoints return a move-only `Path`. A full circle needs the canonical
or angle constructor, not coincident SVG endpoints.

SVG preserves native elliptical arcs. TikZ preserves unrotated native arcs;
rotated arcs fall back to cubic paths. `Arc.to_path()` and `Path.arc()` also use
cubic approximation, with segments of at most 45 degrees (unit-circle radial
error below 5e-6, scaled by the larger radius for ellipses). Circle output is
native in both backends. Quadratics are converted exactly to cubics for TikZ.
This is geometric/paint consistency, not pixel-identical rendering.

## Examples and development

Use pyenv to select Python, then:

```sh
uv sync
uv run python -m examples.geometry.gallery
uv run python -m examples.tutorial.render_all
uv run ruff check .
uv run ruff format --check .
uv run pyright
uv run pytest
```

The gallery writes SVG and a standalone TikZ document under
`examples/output/geometry/`. Tutorial outputs mirror their sources under
`examples/output/tutorial/`. The full tutorial runner also compiles its TeX examples.
TikZ compilation requires an external TeX installation with TikZ and standalone;
it is not a Python runtime dependency. Tests check geometry, arc conversion,
path semantics, XML structure, native dispatch, fallback and real TeX compilation.
The compilation test skips explicitly when `pdflatex` is unavailable. Rendering
examples should also be visually reviewed; no pixel baseline suite is provided.

Layer groups, isolated group compositing, automatic layout/routing, arbitrary
backend-specific options and animation are not implemented. Simple 3D supports
orthographic/perspective polygon projection with BSP splitting for intersections
and cyclic occlusion (without face artwork), plus explicit approximate modes;
see the [visibility tutorial](docs/tutorial/en/26-visibility.md).
Public interfaces are provisional before release. For authoring capture, anchors,
transforms, and viewport policies, follow the tutorial and
[coordinate guide](docs/coordinates.md).


## Combinations, layers, and artwork

A Group is one single-parent spatial unit. Gather is a flat operation set and
can cross layers. Assign Entity/Group instances with `set_layer(int_or_layer)`;
Layer itself controls coverage only. See tutorial chapters
[16–18](docs/tutorial/en/16-editable-groups.md).

[Images](docs/tutorial/en/19-images.md) use explicit millimeter viewports and
contain/cover/stretch fitting. SVG embeds bytes; keep the generated asset folder
beside exported TikZ source. [Gradients](docs/tutorial/en/20-gradients.md) use
normalized local shape bounds. Native text/TeX remain solid-color only; isolated
group opacity and layer groups are outside this stage.

## A component-built microscope

Run `uv run python -m examples.spatial.microscope` to export an assembled
microscope and an exploded component study as SVG, TikZ, and PDF.
The [source](examples/spatial/microscope.py) builds the base, stand, stage,
condenser, and optics with parameterized functions and named nested assemblies.
Edit `make_microscope` for placement, `make_stage` for slide details, and
`make_optics` for objectives and eyepieces. The local `Assembly` recipe is an
example helper, not a public Group3D API. Round parts are faceted polyhedra;
the complete scene uses BSP visibility before becoming a 2D drawing.

The focus drive includes guide rails, a moving rack/saddle, a transverse shaft,
a schematic pinion, and knurled coarse/fine handwheels. `make_focus_drive`
keeps stage brackets and rack travel together. `microscope-focus` exports a
pale simplified reference beside an exposed mechanism detail. Gear teeth and
fine-focus coupling illustrate construction; they are not engineering or
kinematic specifications.
