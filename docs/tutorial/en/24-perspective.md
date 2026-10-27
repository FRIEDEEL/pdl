# 24. Perspective projection

Keep the same 3D construction and replace the camera. Unlike orthographic
projection, perspective makes closer parts larger. The first row compares a
plane carrying the same panel, text and underline; the second compares the same
D10. The orthographic reference stays beside each result.

```{literalinclude} ../../../examples/tutorial/spatial/perspective.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![Orthographic and perspective plane artwork and D10](../../../examples/output/tutorial/spatial/perspective.svg)

[Complete runnable source](../../../examples/tutorial/spatial/perspective.py)

## Position and scale

`PerspectiveCamera` uses the same azimuth, elevation and target as
`OrthographicCamera`. World +z is up; azimuth runs from +x toward +y, elevation
above the xy plane. All distances below are millimeters.

- `distance=100`: distance from the eye to target along the camera axis.
- `focal_length=100`: distance from the eye to the virtual image plane.
- `near=0.1`: minimum allowed distance in front of the eye along that axis.

All must be finite and positive, with `near < distance`. The target projects to
`(0, 0)` and its perpendicular plane has scale `focal_length / distance`.
Setting both distances equal preserves scale there. Moving the eye farther away
while increasing focal length by the same factor weakens perspective while
retaining that scale. Increasing focal length alone enlarges the drawing.

For a world point, let `x`, `y` be its target-relative camera-right/up coordinates,
and `d` its target-relative coordinate toward the eye. The projection is:

```text
axial_distance = distance - d
projected_x = focal_length * x / axial_distance
projected_y = focal_length * y / axial_distance
```

The larger `d` is, the closer the point is. Centroid mode uses this axial depth, not
Euclidean distance to the eye and not the light direction. `camera.eye` gives
the world eye position. `projected.point(...)`, `vertex(...)` and `face_center(...)`
use this same projection; indices still refer to the source geometry.

## Artwork and annotations

`Scene3D.project()` still captures a 2D Authoring snapshot without measuring text.
The eventual Canvas evaluates plane-local layout using its font configuration,
then maps glyph outlines and geometry into perspective. Unlike the orthographic
example, plane-local text is exported as vector paths, not searchable native text.
Lines remain exact lines; Bezier curves, circles and glyph contours become
polylines within 0.02 mm of their projected control hull at the projection's
local scale. Outer 2D scaling also scales this tolerance. No bitmap is generated.

Stroke widths remain Canvas widths; they do not become tapered perspective ink.
Plane artwork currently accepts path-compatible shapes, Text, monochrome TeX
outlines, and their composites, with solid fills. Gradient fills and embedded
images are unsupported; TeX outlines retain the existing TeX-tool requirements.
Keep artwork inside its face yourself; no face-boundary clipping is performed.

Add legends after projection, as in [chapter 21](21-project-3d.md). These stay
ordinary 2D content and can keep native text output. Changing the source or
camera requires a new `project()` call; existing snapshots do not follow edits.

## Deliberate limits

Only polyhedra and planar artwork support perspective in this stage. Sphere and
Cylinder require OrthographicCamera and raise an error with PerspectiveCamera.
All vertices, artwork endpoints and Bezier controls must lie strictly beyond the
near plane. Invalid polyhedron points fail during projection; deferred artwork
can fail during bounds evaluation or export. There is no automatic near/far
clipping. The artwork examples explicitly select approximate centroid sorting;
BSP splitting for polygon-only scenes is covered in [chapter 26](26-visibility.md).

Try changing `distance` and `focal_length` from 55 to 110 together. The plane
approaches its orthographic reference while keeping its target-plane scale.

[Previous: D10](23-d10.md) · [Next: Transparency and depth order](25-depth-order.md)
