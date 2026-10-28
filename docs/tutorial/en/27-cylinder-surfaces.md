# 27. Cylindrical surfaces

Start with the rear half of a cylindrical material, open toward you. We want a
smooth curved wall with open ends, so that a probe can be added inside later.

```{literalinclude} ../../../examples/tutorial/spatial/cylinder_surface.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![An open half-cylinder viewed from its interior](../../../examples/output/tutorial/spatial/cylinder_surface.svg)

[Complete runnable source](../../../examples/tutorial/spatial/cylinder_surface.py)

## Choose the opening in world coordinates

`CylinderSurface` describes only the curved side, with no thickness, end caps or
flat cut face. Dimensions and positions are in millimeters. `base` is the center
of the lower circle; `height` runs along the normalized `axis`.

`radial` defines angle zero and must be perpendicular to `axis`. Its magnitude
is ignored. With the default +z axis and +x radial, positive angles turn toward
+y. Thus `start_angle=90, sweep_angle=180` keeps the x ≤ 0 half. The camera at
azimuth 0 looks from +x into that opening. The default angular range is 0–180°;
choose it explicitly for your intended opening. Sweeps may be positive up to 360°.
Both sides use the same solid color, independent of scene lighting.

`sort_faces=False` chooses manual object order. The surface still paints its own
far branch before its near branch, splitting only at its orthographic silhouette.
These branches use smooth cubic Bezier arcs of at most 45°, with straight axial
edges; they are not polygon facets. The closed 360° side has no artificial seam.
BSP does not process this surface.

## A washer has walls and end caps

A washer is a closed solid with an axial hole, rather than an open side patch:

```{literalinclude} ../../../examples/tutorial/spatial/washer.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![A washer with its central bore open](../../../examples/output/tutorial/spatial/washer.svg)

[Complete runnable source](../../../examples/tutorial/spatial/washer.py)

`AnnularCylinder` requires `0 < inner_radius < outer_radius` and a positive
height. Its visible inner wall, outer wall and facing annular cap are projected
in order. The hole is empty geometry, not a white disk: earlier artwork remains
visible wherever no wall or cap covers it.

![Above, below, side and axial views of washers and open surfaces](../../../examples/output/spatial/material_probe-views.svg)

The orange line is drawn before each washer. It remains visible through the
bore where the viewing direction permits; from the side the outer wall hides it.
The bottom row shows open half-cylinder surfaces at the same camera angles.

## Move geometry before projection

Both types are immutable. Use `dataclasses.replace` to change dimensions, base or
axis, or `.transformed(Transform3D...)` to translate, rotate, reflect or uniformly
scale a copy. A surface's `point(angle, height)` returns a world coordinate for
attachments or labels. Angles use degrees, height uses axial millimeters; the
query does not test visibility or clamp to the authored patch.

Nonuniform scaling, shear and singular transforms are rejected, since they do
not preserve circular cylinders. `axis` and `radial` must remain perpendicular.

These new types, like the existing smooth `Cylinder` and `Sphere`, currently
require **OrthographicCamera**. PerspectiveCamera explicitly raises an error.
They sort as whole objects in centroid mode; intersections with other objects
are not solved. Auto mode warns and uses centroid ordering for the whole scene;
explicit BSP mode rejects curved objects. For deliberate illustration layers,
use separate manual projections as shown next.

[Previous: Intersections and visibility](26-visibility.md) · [Next: Projected layers](28-projected-layers.md)
