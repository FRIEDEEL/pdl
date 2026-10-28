# 29. Editable entities and explicit reference frames

`Circle`, `Line`, `Path`, `Text`, `TeX`, `Node`, `Connection`, `Image`,
`ProjectedScene`, and `Group` share the `Entity` authoring base. Operate on
concrete objects directly; a separate `Entity(shape)` wrapper is unnecessary.
Geometry parameters describe local content. Transforms edit placement and return
the same object. Use `copy()` to retain an independent editable version.

## Keep a reference frame fixed, or move it explicitly

A `Frame` contains an origin and two basis vectors. Defaults are `(0, 0)`,
`(1, 0)`, and `(0, 1)`: the world-aligned unit frame. A local pair `(u, v)` means
`origin + u * x_basis + v * y_basis`. Basis vectors can include scale and skew.
The origin and vector components use authoring millimeters.

Every entity exposes an independent `frame`; assigning one changes the reference
only, not the object's placement. Transforming the object does not change its
frame. Explicitly collect both objects in a `Gather` to transform them together.

```{literalinclude} ../../../examples/tutorial/geometry/reference_frames.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![Fixed frame on the left and explicitly rotated frame on the right](../../../examples/output/tutorial/geometry/reference_frames.svg)

[Complete runnable example](../../../examples/tutorial/geometry/reference_frames.py)

Both panels retain gray original outlines and axes. On the left, only the box
rotates. On the right, the box and frame rotate together because the Gather
contains both. `about=box.frame.origin` chooses one shared world-space pivot;
it does not bind the frame to the box.

## Positions, pivots, and capture

- `translate(x, y)` adds a world-space displacement.
- `rotate(angle, about=...)` uses counterclockwise degrees; `scale(x, y,
  about=...)` allows nonuniform stretch. Pivots may be world coordinate pairs,
  captured anchors, or explicit frame points.
- Without a pivot, ordinary objects use their transformed local bounds center;
  Groups use visible group bounds. Frames use their own origin. Gather uses
  the world origin unless a shared pivot is supplied.
- `frame.point(u, v)` and `frame.vector(u, v)` express positions and displacements.
  A position assigned with `move_to(frame.point(...))` follows that frame until
  a capture or subsequent placement operation. This is an explicit dependency.
- `anchor(...)` retains its existing snapshot semantics. It describes the state
  at the call, with measurement deferred; subsequent edits do not move that anchor.
- `draw()` captures state and references; later edits do not alter that record.
  Text measurement and layout evaluation can still wait until rendering.

`center=` remains a compatibility alias for `about=`; pass only one. For
`Path`, `move_to` keeps its path-building meaning; use `place(...)` to position
the whole path. Other entities support both `move_to` and `place`.
Geometry and glyphs follow affine transforms, while stroke widths stay in canvas
millimeters. A nonuniform scale stretches glyphs as well as geometric shapes.

## Non-painting references

`Frame` and `ReferencePoint` are entities and may belong to Groups or Gathers.
They emit no paint, contribute no visible bounds or automatic viewport extent,
and produce no occlusion geometry. They also do not enter 3D BSP calculations.
Calling `draw(frame)` is harmless and produces no visible content, subject to
the ordinary rule that grouped members are drawn through their outermost Group.

`frame.visualize(...)` returns an independent drawable Group. Axis length,
origin-marker radius, and axis/marker styles are arguments; none are frame data.
`axis_length` is measured in local units, so basis magnitudes affect display.
The returned visualization captures the frame at the call and does not follow
later edits. Its visible contents contribute to ordinary bounds and paint order.

## Migrating older code

Replace `Entity(Circle(...), style=paint)` with `Circle(...).set_style(paint)`.
`Entity(geometry, space=...)` remains a compatibility adapter for existing
`CoordinateSystem`/Canvas mapping workflows. Its omitted rotation/scale pivot
retains the historical world-origin default; direct concrete objects use their
own center. Specify `about=(0, 0)` when migrating an intended world-origin
operation. Existing `Drawing` descriptions and immutable `CoordinateSystem`
identities remain supported; they are separate from editable `Frame` references.
`Group.transformed(...)` still creates a captured description; prefer
`group.copy().apply_transform(...)` when another editable group is needed.

A Group still exclusively owns its members, and Gather remains a flat operation
set. There is no general-purpose parent/child API on ordinary entities.

API: {py:class}`pdl.Entity`, {py:class}`pdl.Frame`,
{py:class}`pdl.ReferencePoint`, {py:class}`pdl.Gather`.

---

[Previous: Projected layers](28-projected-layers.md)

Bounds queries, and reparenting that must preserve a text-dependent world pose,
require an active typography context when their measurements cannot be deferred.
