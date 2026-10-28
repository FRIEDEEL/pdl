# 26. Intersections and visibility

A whole face cannot always be painted entirely before or after another face.
Two intersecting panels exchange front/back relation across the intersection.
Neither their center depths nor their maximum depths can represent that change.
Keep the centroid reference beside the result to see the difference:

```{literalinclude} ../../../examples/tutorial/spatial/visibility.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![Same intersecting panels: centroid reference and BSP visibility](../../../examples/output/tutorial/spatial/visibility.svg)

[Complete runnable source](../../../examples/tutorial/spatial/visibility.py)

## From 3D fragments to 2D Authoring

`Scene3D.project()` defaults to `visibility="auto"`. When every object is a
Polyhedron without face artwork, it uses BSP (binary space partitioning):

1. Select a face's supporting plane and classify other polygons by half-space.
2. Split polygons crossing that plane; recursively partition the two sides.
3. Traverse far side, coplanar faces, near side relative to the camera.
4. Project the ordered fragments into ordinary 2D Authoring drawings.

The same procedure works with orthographic and perspective cameras. Simple
concave face loops are triangulated first when necessary; convex faces remain
intact until a partition crosses them. New triangulation and BSP edges are not
stroked. Input object order, then face order, determines coplanar tie priority;
later sources are painted on top. No back faces are discarded.

Add legends, leaders and layout **after** projection as before. Vertex and
face-center queries retain original indices. `projected.source_faces` maps each
current drawing child to its `(object_index, face_index)`; several fragments can
refer to the same face. `reordered()` also reorders this mapping and marks the
snapshot's `visibility` as `"manual"`.

## Intersections, cycles and opacity

BSP handles both intersecting faces and cycles such as A covering B, B covering C,
and C covering A in different overlap regions. The latter can occur even without
physical intersection. Splitting creates a valid order of smaller pieces.
`Polyhedron.opacity` remains ordinary back-to-front compositing per face/fragment;
it does not model refractive glass or create new boolean solids.

The [larger example](../../../examples/spatial/visibility.py) shows parallel-face
ordering errors, crossings, a three-ribbon cycle and transparent intersections.

![Four centroid/BSP comparisons](../../../examples/output/spatial/visibility.svg)

## Explicit scope and safeguards

- `visibility="bsp"` requires the supported polygon-only scene. Curved solids,
  free Plane3D artwork and face artwork raise an error in this mode.
- In `"auto"`, those scenes select **whole-scene approximate centroid sorting**
  with a warning. Write `visibility="centroid"` explicitly when that approximation
  is intended. `projected.visibility` reports the selected algorithm.
- `sort_faces=False` bypasses sorting and splitting, regardless of visibility.
  Manual reordering cannot solve a whole-face cycle.
- `bsp_tolerance=1e-8` is a positive finite **absolute world-plane tolerance in
  millimeters**. This is floating arithmetic, not exact predicates; very small
  gaps can become coplanar ties. Rescale extreme geometry or choose a suitable
  tolerance. Near-plane crossing still raises an error, rather than clipping.
- `max_fragments=100000` counts triangulation plus BSP fragments. Exceeding it or
  the internal tree-depth limit of 500 raises an error without approximate fallback.
  Partitioning may split disjoint polygons because supporting planes are infinite;
  heavily overlapping inputs can produce many fragments and increase output time.

[Previous: Transparency and depth order](25-depth-order.md) · [Next: Cylindrical surfaces](27-cylinder-surfaces.md)
