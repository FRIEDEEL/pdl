# pdl — Python Drawing Library

A small, typed Python library for static vector drawings. Stage 1 provides
basic geometry, compound paths, solid fill/stroke and SVG/TikZ output without
runtime dependencies. Python 3.12 or later is required.

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
- Objects render in insertion order. Native shape identity is retained until
  backend dispatch; unsupported geometry falls back through `to_path()`.
- Paths are mutable builders. The canvas reads them at export time; use
  `path.to_path()` to take an independent snapshot before adding it.
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
uv run python examples/gallery.py
pdflatex -interaction=nonstopmode -halt-on-error -output-directory examples/output examples/output/gallery.tex
uv run ruff check .
uv run ruff format --check .
uv run pyright
uv run pytest
```

The gallery writes SVG and a standalone TikZ document to `examples/output`.
TikZ compilation requires an external TeX installation with TikZ and standalone;
it is not a Python runtime dependency. Tests check geometry, arc conversion,
path semantics, XML structure, native dispatch, fallback and real TeX compilation.
The compilation test skips explicitly when `pdflatex` is unavailable. Rendering
examples should also be visually reviewed; no pixel baseline suite is provided.

Stage 1 excludes text, images, layers/groups, transforms on arbitrary objects,
anchors, dependency expressions, automatic layout, backend-specific option
passthrough, animation and 3D. Public interfaces are provisional before release.
