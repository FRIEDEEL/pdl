# 5.4 Transparency and depth order

Polygon-only scenes now use BSP splitting by default; the next chapter explains
intersections and cyclic visibility. Both cameras retain back faces. The upper
comparison keeps an opaque cube beside the transparent result; its rear edges
become visible. The lower free-plane artwork comparison explicitly selects
approximate centroid sorting to demonstrate paint-order effects.

```{literalinclude} ../../../../examples/tutorial/spatial/depth_order.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![Transparent faces and automatic versus manual paint order](../../../../examples/output/tutorial/spatial/depth_order.svg)

[Complete runnable source](../../../../examples/tutorial/spatial/depth_order.py)

## Automatic order

Pure polyhedra without artwork use BSP by default, including transparent faces.
For the free Plane3D drawings here, `visibility="centroid"` explicitly chooses
approximate depth ordering by the `depth_point` reference (local `(0, 0)` by
default). Face artwork in that mode travels with its face as one whole item.
The axis depth is not Euclidean distance to the camera.

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
painted first. In manual mode each child is one complete face plus its artwork, or one other
scene object. BSP snapshots instead contain fragments with `source_faces` mappings. Starting with `sort_faces=False` makes the indices follow source
object/face order. Point and face-center queries keep their original source
indices after reordering. The `restored` snapshot in the source demonstrates
reversing the two manual items without changing their geometry.

## Scope boundaries

Approximate centroid ordering can fail even for disjoint faces. Manual reordering
cannot solve whole-face visibility cycles. BSP handles supported polygon scenes
by splitting them; see [Intersections and visibility](05-visibility.md) for the
algorithm, tolerances and limits. Separate scenes follow ordinary Canvas/Layer
order. Curved solids remain orthographic-only; curved surfaces, free planar
artwork and face artwork require approximate or manual order.

Try changing the orange opacity from 0.55 to 1, then reversing the manual objects.
The same geometry produces a different overlap because the paint order changed.


---

[Part contents](index.md)
