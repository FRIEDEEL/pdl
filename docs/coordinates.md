# Authoring state, coordinate spaces, and resolution

## Object responsibilities

Geometry values (`Rectangle`, `Circle`, `Polygon`, and numerical `Path` commands)
express local shapes. `Entity` is the editable authoring handle for placement
and optional instance style. `Drawing` remains the immutable placement record;
`Group` defines ordered reusable content. Existing direct geometry drawing is
supported. Use `Entity` when in-place operations are needed:

```python
from pdl import Canvas, Circle, Entity, Rectangle

canvas = Canvas(100, 60)
a = Entity(Rectangle((-10, -5), 20, 10)).move_to((30, 20))
b = Entity(Circle((0, 0), 3)).move_to(a.anchor("west"))
a.translate(30, 0)
canvas.draw(b)
canvas.draw(a)
canvas.save("drawing.svg")
```

`move_to` places the transformed local bounds **center** at the supplied point.
`transform`, `translate`, `rotate`, `scale`, and `reflect` mutate the handle and
return it. Each new transform applies in authoring world outside the previous placement; rotation
is about the authoring world origin unless `center` is supplied. Shape geometry is not
rewritten. To move a connected assembly together, place it inside a `Group`.
Group transforms do not recalculate member spacing.

`Entity.anchor()` and `Entity.space` capture the current authoring state without
measuring it. Later edits do not change those captures. `Canvas.draw()` captures
built-in mutable descriptions, including shared paths, without measuring fonts.
Unreferenced old states can be released. Custom `Composite` implementations must
provide immutable descriptions; arbitrary mutable user objects are not frozen
by this protocol. Direct numerical geometry keeps its existing value API.

A reference captures a description, not a numerical result: changing the canvas's
default font before another render can change measured positions. An explicit
`canvas.resolve(object)` instead fixes typography, coordinates and transforms.

## Spaces and vectors

The default authoring world is Cartesian millimeters, origin at bottom-left,
x right, y up. Canvas backend axis conversions are private to adapters.

```python
from pdl import WORLD, CoordinateSystem, Transform

root = CoordinateSystem(name="diagram")
local = root.child(Transform.translate(20, 10) @ Transform.rotate(30))
a = Entity(Rectangle((-5, -5), 10, 10), space=local)
b = Entity(Circle((0, 0), 2)).move_to(a.space.point(12, 0))
canvas.map(root, Transform.translate(10, 5))
```

An unqualified `move_to((x, y))` uses the entity's parent frame. A space point or
anchor reference is converted from its own frame. An entity frame represents
its original numerical geometry coordinates after all placement operations;
its origin is not implicitly the shape's bounds center. `space.child()` supports
nested frames. Unmapped roots coincide with world. `canvas.map(frame, matrix)`
overrides that frame's local-to-parent matrix for this canvas only;
`canvas.map(WORLD, matrix)` sets the final world-to-canvas base mapping.

`anchor("east")` means the local shape anchor transformed into world, not the
east anchor of its world axis-aligned bounds. Compare:

```python
shape_tip = canvas.query().point(a.anchor("east"))
box_tip = canvas.query().bounds(a).anchor("east")
local_offset = a.anchor("east").shifted(a.space.vector(5, 0))
world_offset = a.anchor("east").shifted(WORLD.vector(5, 0))
```

Legacy `anchor + (x, y)` offsets retain their referencing-space semantics.
For Entity placements at the root this is authoring world. Explicit vectors
remove ambiguity. Translation affects points, but not vectors. Inverse
conversions through singular matrices raise `ValueError`; forward geometry
can still be degenerate. `Transform` also supplies inverse, determinant, shear,
reflection about a line, and `around(center)` for pivoted transformations.

## Resolution and queries

`draw` order determines paint order, independently of dependency evaluation.
Measuring A to position B does not draw A. Dependencies are cached within one
operation; another render/query reevaluates them under its own configuration.

- `canvas.query().point(reference)` returns a numerical Canvas point.
- `canvas.query().bounds(object)` returns layout/geometry bounds without stroke.
- `canvas.query().ink_bounds(object)` uses glyph outlines rather than layout boxes.
- `in_space=some_frame` requests authoring coordinates before viewport adaptation.
- `canvas.query().from_canvas(point, in_space=frame)` converts a numerical Canvas
  point back to a fixed authoring coordinate; it does not restore dependencies.
- `canvas.resolve(object)` returns a detached `ResolvedGraphic` in Canvas coordinates.

Queries do not add objects to the paint list. For fit/auto-size, the current
paint list determines the viewport. When the list is empty, a bounds query or
resolve uses the requested object as its fitting content; a point/vector query
has no fitting content and uses the base mapping. Thus defining the scene before
querying final Canvas positions is recommended. Explicit authoring-space queries
do not need a fitted viewport.

Resolved results retain rectangles/circles, affine placement, measured native
Text/TeX and Nodes. Composite definitions become concrete ordered groups.
Adapters select native output before lowering unsupported constructs. This is
two data representations plus output adapters, not parallel class hierarchies
for every shape. Text and TeX use measured subclasses to reuse existing adapters.
Font resources and external TeX installations remain required by native output.
Resolved snapshots can be drawn on another canvas; that destination's viewport
mapping then applies to their concrete geometry like any other drawing.

## Viewport modes

```python
Canvas(100, 60, mode="clip")
Canvas(100, 60, mode="fit", padding=5)
Canvas(mode="auto_size", padding=5)
```

- `clip` is the default: fixed viewport, no implicit scaling, overflow clipped.
- `fit` keeps a fixed viewport, scales content uniformly, and centers it.
- `auto_size` preserves drawing scale and chooses dimensions from content plus padding.

All modes apply the explicit world mapping first. Fit/auto-size then derive a
final mapping from resolved bounds. Glyphs scale with geometry; stroke widths
remain in Canvas millimeters. Bounds include layout boxes; fitting reserves a
conservative stroke allowance, including miter joins. It is not an exact painted
outline measurement. Empty geometry does not introduce the origin into bounds;
empty bounds have `is_empty=True` and no anchor. An empty auto-size canvas uses
a 1 mm viewport; point-sized content uses a positive minimum extent.

This stage has no relative-to-viewport authoring units, so viewport-size cycles
cannot arise through built-in coordinates. Nonlinear frames, exact stroke bounds,
automatic layout/routing, curve lengths, closest points and general intersections
remain future work.

The example `examples/coordinates/relationships.py` demonstrates captured
attachments, new attachments after movement, reflection/rotation of assemblies,
font-dependent labels and all three viewport policies.
