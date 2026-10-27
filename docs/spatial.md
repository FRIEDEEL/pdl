# Simple 3D drawings

Define geometry in right-handed 3D coordinates, then project it into an ordinary
2D `Canvas`. Lengths use millimeters and rotation angles use degrees with the
right-hand rule. SVG and TikZ share the same projected polygons and face colors.
There are no additional runtime dependencies.

## Solids, camera and light

```python
from pdl import (
    Canvas,
    Color,
    DirectionalLight,
    OrthographicCamera,
    Scene3D,
    Vector3D,
    regular_polyhedron,
)

solid = regular_polyhedron("dodecahedron", radius=20, color=Color(0.38, 0.73, 0.91))
scene = Scene3D(
    (solid,),
    camera=OrthographicCamera(azimuth=30, elevation=22),
    light=DirectionalLight(direction=Vector3D(-1, 1, -2), ambient=0.22),
)
canvas = Canvas(60, 60, mode="fit", padding=5)
canvas.draw(scene)
canvas.save("solid.svg")
```

`regular_polyhedron` supports `tetrahedron`, `cube`, `octahedron`, `dodecahedron`
and `icosahedron`. All use a positive **circumradius**, not an edge length.
`Polyhedron(vertices, faces)` accepts custom indexed faces. Each face must be a
simple convex planar polygon, counterclockwise when viewed from outside. Winding
controls the surface normal. Topology and intersections between faces are not checked.
Use `face_colors` to provide one intrinsic color per face. `transformed()` returns
a new solid and preserves outward winding under reflections; normals are computed
from the transformed vertices, including nonuniform scaling.

The orthographic camera looks toward `target`, which projects to `(0, 0)`.
World +z is up. Azimuth runs from +x toward +y, and elevation is above the xy plane.
Default angles provide an isometric view. The camera preserves millimeter scale;
place the resulting scene using an ordinary 2D `Drawing`/`Transform`, or fit it.
A scene can coexist with ordinary 2D annotations.

Light `direction` is the **direction in which light travels**, in world coordinates,
not the direction from the surface toward the source. Let `n` and `d` be normalized
world face normal and light direction:

```text
intensity = ambient + (1 - ambient) * max(0, -dot(n, d))
face_rgb = intrinsic_rgb * intensity
```

A face pointing toward the source receives full intrinsic color; a perpendicular
or backward-facing face receives ambient color. `ambient` is in `[0, 1]`, default
`0.25`. Direction magnitude has no effect. Camera motion does not change face
lighting. This is a direct RGB diagram mapping without gamma conversion, cast
shadows, specular highlights or distance attenuation. Set `Scene3D(light=None)`
to use unmodified intrinsic colors.

## All five regular polyhedra

Run `uv run python -m examples.spatial.platonic_solids`. The example writes SVG,
TikZ source and compiled PDF under `examples/output/spatial/platonic_solids.*`.
Edit `CAMERA`, `LIGHT` and `BASE_COLOR` at the top to compare directions and colors.

```{literalinclude} ../examples/spatial/platonic_solids.py
:language: python
```

![All five Platonic solids](../examples/output/spatial/platonic_solids.svg)

## Coordinate frames and 3D planes

`Transform3D` supports translation, uniform/nonuniform scaling, arbitrary-axis
rotation, composition and inversion. `a @ b` applies b first. Singular transforms
can map points forward but cannot be inverted; collapsed faces are rejected.
`CoordinateSystem3D.child()` creates nested immutable frames. `convert_point()`
includes translation; `convert_vector()` ignores it. These frames are independent
of 2D `CoordinateSystem` and Canvas mappings. Convert to world coordinates before
constructing scene geometry.

`Plane3D(origin, u, v)` embeds local `(x, y)` as `origin + x*u + y*v`. Independent
basis vectors may be nonorthogonal or nonunit. The plane normal is normalized
`u.cross(v)`. The infinite plane is not itself drawn: `plane.place(graphic, style)`
puts finite 2D geometry, groups or labels into it. Projection is an affine mapping,
so circles become ellipses and text follows the plane. Canvas captures built-in
mutable paths/entities inside the scene at `draw`, as in 2D drawings.

Planar artwork retains its own styles. For a lit panel, choose its fill explicitly
with `light.shade(intrinsic_color, plane.normal)`; child artwork is not recolored.
A planar drawing sorts as one item by its plane origin unless a local
`depth_point=(x, y)` is supplied. Its internal 2D drawing order is preserved.

Run `uv run python -m examples.spatial.planes` for a tilted panel and a marker
whose world location is converted through nested frames.

```{literalinclude} ../examples/spatial/planes.py
:language: python
```

![Plane placement](../examples/output/spatial/planes.svg)

## Occlusion limits

Within one `Scene3D`, faces from all solids are sorted together by centroid depth,
far to near, with stable input order on ties. Planar drawings participate using
their explicit depth references. Separate scenes follow Canvas drawing order.

This painter algorithm does not split intersecting faces or resolve cyclic
occlusion. Overlapping depth intervals can produce incorrect order. No automatic
hidden-edge dashes, transparency solver, perspective, backface culling or geometric
clipping is provided. Closed opaque convex solids are the intended first use.
For manual ordering, set `sort_faces=False` and arrange objects/faces yourself.
