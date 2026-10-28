# 5.1 Project 3D, then draw in 2D

A 3D scene chooses a camera and light. Call `project()` to obtain a 2D authoring
snapshot, then add ordinary drawing objects before Canvas resolves the result.
The snapshot is not a rendered image or a Resolved result.

```{literalinclude} ../../../../examples/tutorial/spatial/projection.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![A projected cube with a 2D legend](../../../../examples/output/tutorial/spatial/projection.svg)

[Complete runnable example](../../../../examples/tutorial/spatial/projection.py)

`regular_polyhedron` uses a circumradius in millimeters. The orthographic camera's
azimuth runs from world +x toward +y; elevation is above the xy plane. Default
world +z is up. Projection preserves length scale without perspective shortening
by distance. Face colors use the scene's parallel light and ambient term.

`projected.vertex(0, 7)` addresses vertex 7 of source object 0; painter sorting
does not change these indices. It returns a fixed local 2D point. The leader and
legend are created afterward, so their text stays in the drawing plane. The final
Group rotation affects the projection, leader and legend together. Applying a
transform only to the projected drawing would not move these fixed coordinates.

Projection captures built-in mutable paths/entities in the source scene. It does
not measure text. Font-dependent layout and bounds resolve later with the Canvas
renderer. Changing the camera or source needs a new `project()` call; existing
snapshots do not update. `point(Point3D(...))` projects any world point with the
same camera, and `face_center(object_index, face_index)` returns a face's projected
vertex average. These methods do not test visibility. `projected.anchor()` instead
provides the ordinary deferred bounds anchors used in earlier chapters.

The supported order is **3D Authoring → 2D Authoring + legends → Resolved → backend**.
Use explicit projection when composing 2D annotations. Polygon-only scenes use BSP splitting
for intersections and cycles; [related chapter](05-visibility.md) explains visibility
and the explicit approximate modes for artwork and curved solids.

Try changing the camera elevation and rerunning. Then rotate the complete Group
by a different 2D angle and observe that the annotation remains attached.


---

[Part contents](index.md)
