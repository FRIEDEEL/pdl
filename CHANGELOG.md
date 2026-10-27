# Changelog

## Unreleased

### Added

- Basic lines, polylines, circles, rectangles, polygons, elliptical arcs and
  quadratic/cubic paths with explicit closing and multiple subpaths.
- Solid RGB fill and stroke, fill rules, line caps and joins.
- Ordered, fixed-size millimeter canvas with SVG and standalone TikZ exports.
- TikZ-style and SVG-style arc constructors, a dual-backend gallery and tests.
- Deferred anchor references for connections and relative node positions,
  including anchors on explicitly placed component children.
- Native TikZ node shapes for translation and rotation, with general
  decomposition for SVG and other affine placements.
- Automatic default fonts for initial renders and examples comparing font
  choices on the same authoring objects.

- Mutable `Entity` authoring handles with captured anchor/space descriptions,
  independent draw records, and in-place placement transformations.
- Nested Cartesian coordinate systems, canvas-specific mappings, explicit
  space points/vectors, inverse transforms, pivoted transforms, shear and reflection.
- Canvas-bound queries, fixed resolved snapshots retaining native object identity,
  text ink bounds, and Canvas-to-authoring point conversion.
- `fit`, `auto_size`, and default `clip` viewport policies with padding, plus a
  square/triangle/circle example demonstrating captured and renewed attachments.
- Analytic affine circle/elliptical-arc bounds and explicit empty bounds.

### Changed

- **Breaking:** `Node.anchor()` and `Group.anchor()` return `AnchorRef` instead
  of coordinate snapshots. `Canvas.anchor()` has been removed. Define
  relationships with object or instance anchors; use `Canvas.bounds()` for
  explicit numerical layout bounds.
- Content sizes and dependent endpoints are recalculated on each render,
  using that invocation's font configuration. Paint order remains unchanged.
- Backends select supported native objects before general decomposition.

- **Breaking:** drawing a mutable built-in `Path` now captures its commands;
  later edits require another `draw` call. Immutable geometry retains identity.
- `Canvas.bounds()` now returns final Canvas coordinates by default; request
  `canvas.query().bounds(object, in_space=WORLD)` for authoring world coordinates.
- Rendering now resolves dependencies through a common stage before adapter dispatch.

### Limitations

- Generic arc lowering and rotated TikZ arcs use cubic approximation.
- Layers, automatic routing, general constraint solving and arbitrary
  backend-specific options remain outside this stage.
- Native SVG and LaTeX text metrics may differ slightly. Default font coverage
  depends on the installed fonts; explicit font stacks remain available.
- Fitted viewports reserve conservative stroke margins rather than exact painted
  bounds. Text scales with geometry; stroke widths stay in Canvas millimeters.
- Custom composites must provide immutable descriptions. Nonlinear frames,
  curve lengths, closest-point queries and general intersections are deferred.
