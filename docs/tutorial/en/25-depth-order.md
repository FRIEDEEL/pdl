# 25. Transparency and depth order

Depth sorting is an approximation for diagrams. Both orthographic and perspective
scenes retain all polygon faces, including back faces. The upper comparison keeps
an opaque cube beside the transparent result; its rear edges become visible.
The lower comparison shows why transparent overlap depends on paint order.

```{literalinclude} ../../../examples/tutorial/spatial/depth_order.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![Transparent faces and automatic versus manual paint order](../../../examples/output/tutorial/spatial/depth_order.svg)

[Complete runnable source](../../../examples/tutorial/spatial/depth_order.py)

## Automatic order

Within a Scene3D, each face is sorted by the average of its vertices along the
camera axis, far to near; ties preserve input order. Its face artwork travels
with it as one item, retaining its own internal drawing order. A Plane3D placement
uses its `depth_point` reference (local `(0, 0)` by default), so choose a suitable
local center for off-center artwork. Sorting does not compare Euclidean distance,
projected overlap regions, or individual sightline intersections.

`Polyhedron.opacity` defaults to 1 and accepts values in `[0, 1]`. It applies
independently to each face's fill and stroke. This is ordinary compositing,
not physical glass, refraction, or isolated whole-solid opacity. Face artwork
retains its own opacity: use explicit artwork styles if its numbers should also
be translucent. Back-face artwork is retained, seen mirrored from behind;
edge-on artwork may collapse. An opaque face painted later naturally covers it.
Planar drawings use their ordinary `Style(opacity=...)`.

## Manual order

Set `sort_faces=False` to preserve object order, then each solid's supplied face
order. In the example the near orange panel is deliberately listed before the
far blue panel. Automatic sorting corrects that order on the left; manual mode
retains it on the right, so blue is painted on top.

For an explicit global override, use `projected.reordered(order)`. The tuple must
be a permutation containing every current child index exactly once; index 0 is
painted first. Each child is one complete face plus its artwork, or one other
scene object. Starting with `sort_faces=False` makes the indices follow source
object/face order. Point and face-center queries keep their original source
indices after reordering. The `restored` snapshot in the source demonstrates
reversing the two manual items without changing their geometry.

## Known failure cases

Faces are assumed not to intersect. Overlapping depth intervals can still cause
incorrect center sorting even without intersections. Cyclic occlusion has no
correct whole-face paint order; manual reordering cannot solve that case either.
No cycle detection, splitting, local clipping or exact transparency solver is
performed. Separate projected scenes follow ordinary Canvas/Layer order.
Smooth spheres/cylinders remain orthographic-only and sort as whole objects;
the polygon-face back-face and opacity rules here do not extend their APIs.

Try changing the orange opacity from 0.55 to 1, then reversing the manual objects.
The same geometry produces a different overlap because the paint order changed.

[Previous: Perspective](24-perspective.md)
