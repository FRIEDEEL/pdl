# Changelog

## Unreleased

### Fixed

- Flowchart cardinal-port connections now default to orthogonal elbows. Removed
  accidental node offsets and fixed-coordinate routes from the growing example.
  Explicit waypoints remain authoritative; `route="straight"` opts into direct lines.

### Added

- A bilingual Group/Layer/Gather comparison chapter with a shared-member
  example showing how overlapping selections change one another's arrangement.

- Layer.upper/lower read current adjacent layers without creating them; missing
  neighbors, including on unattached layers, return None.

- Explicit `Scene3D.project()` snapshots into ordinary 2D Authoring, with source
  vertex/face-center correspondence and deferred bounds anchors for 2D legends.
- Plane-local vector face artwork, transported with polyhedron transforms and
  sorted with its face. Includes a numbered D10 example and three bilingual
  tutorial steps with actual SVG/PDF output.
- Simple concave planar face loops; self-crossing, touching and zero-length
  face edges are rejected. Whole-shell closure remains a separate concern.

- Smooth 3D cylinders and spheres with portable SVG/TikZ/PDF vector gradients.
  Cylinders sample directional Lambert shading; spheres use an explicit radial
  lighting approximation. Includes light-direction and limiting-view examples.

- 3D Cartesian frames and affine transforms, orthographic projection, planar
  placement of 2D drawings, indexed polygonal solids and all five Platonic solids.
  Directional flat shading maps intrinsic RGB color using oriented face normals;
  centroid depth sorting produces SVG/TikZ vectors without face intersections.

- Growing flowchart components: editable FlowNode, Decision, Terminal and FlowEdge,
  font-aware directional placement, merges and feedback, and isolated draw captures.
  Includes a bilingual guide and an SVG/TikZ/PDF example.

- Editable single-parent Groups with add/remove/dismiss, world-preserving
  reparenting, and flat overlapping Gather selections with promotion warnings.
- Canvas-owned Layer identities with integer lookup, insertion/reordering,
  per-record layer capture, and Layer.to_gather for imperative operations.
- Captured PNG/JPEG images with contain/cover/stretch fitting, embedded SVG,
  and portable TikZ image sidecars.
- Linear/radial RGB gradient fills in local normalized bounds and per-leaf
  opacity, with native SVG resources and PDF functional shading output.
- Five bilingual tutorial chapters and six runnable examples for editable
  groups, Gathers, layers, images, gradients, and opacity; expanded API reference.

### Changed

- Breaking: LayerStack insertion and movement methods now use spatial names:
  `insert_below`/`insert_above` and `move_below`/`move_above` replace the former
  before/after methods. Update callers; the old names have been removed.

- Group is now editable. Existing Drawing-based component definitions remain
  supported and create independent instances; live Entity/Group members use
  single-parent ownership. Mutating Group methods affect future captures only.
- Breaking: individual grouped members cannot be submitted directly to Canvas;
  draw the outermost Group, or remove/dismiss a member first. Gather and layer
  assignments to grouped children promote to the outermost Group with a warning.
- Grouping across layers moves the assembly to the highest member layer unless
  overridden. Dismiss retains its current layer rather than restoring old layers.
- Independent Layer instances are separate identities, even at equal initial
  positions; use canvas.layers[index] for canonical canvas-local lookup.


- A local Sphinx/MyST documentation site with Furo, Google-style docstring
  extraction, and a reference for all public exports. Build dependencies live
  in the optional `docs` group; tutorial assets are generated during the build.
- English and Chinese tutorials on paint order, text/TeX, transforms, authoring
  frames, anchors, groups, paths, queries, viewports, resolution, and fill rules,
  with runnable examples and rendered comparisons.

- English and Chinese step-by-step tutorials covering a Hello world node,
  basic shapes, coordinate guides, strokes and fills, with seven runnable SVG examples.

- Optional TikZ PDF compilation during `Canvas.save`, with auto/source/required
  modes and configurable intermediate-file retention; examples use the same pipeline.

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
