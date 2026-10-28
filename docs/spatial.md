# Simple 3D drawings

Define geometry in right-handed 3D coordinates, then project it into an ordinary
2D `Canvas`. Lengths use millimeters and rotation angles use degrees with the
right-hand rule. SVG and TikZ share the same projected polygons and face colors.
There are no additional runtime dependencies.

## The authoring boundary

`scene.project()` explicitly returns a `ProjectedScene`, an ordinary 2D authoring
composite. Projection captures built-in mutable descriptions and fixes camera,
light, geometry and painter order. It does not measure text or resolve 2D layout.
Add legends, guides and connections afterward; Canvas resolves that combined 2D
authoring description into Resolved before SVG/TikZ output.

`projected.vertex(object_index, vertex_index)`, `face_center(object_index,
face_index)` and `point(world_point)` return fixed **local 2D millimeter points**.
Indices retain input order despite face sorting. They are not visibility queries
or live references to a moved instance. Group the projected drawing and its 2D
annotations to transform them together. Change the camera by creating a new
projection; previous projections remain unchanged. `projected.anchor()` provides
ordinary deferred bounds anchors. Non-polyhedron entries have no vertex/face data.

Direct `canvas.draw(scene)` remains a compatibility shorthand for the same
projection path; new code should make the projection boundary explicit.

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
canvas.draw(scene.project())
canvas.save("solid.svg")
```

`regular_polyhedron` supports `tetrahedron`, `cube`, `octahedron`, `dodecahedron`
and `icosahedron`. All use a positive **circumradius**, not an edge length.
`Polyhedron(vertices, faces)` accepts custom indexed faces. Each face must be a
simple planar polygon, counterclockwise when viewed from outside. Winding
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
puts finite 2D geometry, groups or labels into it. Orthographic projection is an affine mapping,
so circles become ellipses and native text follows the plane. Perspective
projection instead outlines and maps plane content as vector paths. Canvas captures built-in
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

## Plane-local face artwork and a D10 example

`solid.face_plane(i)` returns a unit chart centered at the average of that face's
vertices. Its local v points toward world +z projected into the face; horizontal
faces use their first edge as u. `solid.with_face_artwork(i, graphic, style=None,
transform=Transform())` returns a new solid with that face's 2D artwork replaced.
Text, paths and Groups are allowed; no raster texture is required.

Artwork is captured at projection, stays paired with its face during sorting,
and uses the complete plane affine transform. Text measurement still happens
in the later 2D evaluation. Back-facing artwork is retained and mirrored; edge-on artwork may collapse.
Artwork is not automatically shaded or clipped to the face boundary. Keep
it within the face; use explicit text paint. Geometry transforms transport its
physical placement, including scaling and reflection.

The [D10 example](../examples/spatial/d10.py) constructs a pentagonal
trapezohedron from 12 vertices and 10 planar kite loops. It generates centered
number artwork for faces 1-10, projects two opposite views, then adds an ordinary
2D annotation. D10 is an example, not a new library primitive or canonical
numbering convention. No half-space constructor or general boolean union is
introduced here.

![D10 face artwork and 2D legend](../examples/output/spatial/d10.svg)

See tutorial chapters [21](tutorial/en/05-spatial/01-projection.md),
[22](tutorial/en/05-spatial/02-plane-artwork.md) and [23](tutorial/en/07-recipes/01-d10.md).

## Smooth cylinders and spheres

`Cylinder(base=Point3D(...), radius=10, height=25, axis=Vector3D(0, 0, 1))`
defines a closed circular cylinder. The base is a disk center; height is positive,
and the nonzero axis points toward the top (its magnitude is ignored).
`Sphere(center=Point3D(...), radius=10)` defines a sphere. Both accept intrinsic
`color`, silhouette `stroke` (or `None`) and Canvas-millimeter `line_width`.
Dimensions must be finite and positive. Add either object to `Scene3D.objects`,
then call `project()` before composing the resulting 2D drawing.
Orient a cylinder with its axis; general affine ellipsoids are not supported.

These objects use **smooth vector gradients, not surface tessellation**:

- Cylinder: the visible side is one curved patch. Its 33 linear-gradient stops
  sample the world-normal Lambert formula across the projected width, remaining
  constant along the axis. The facing cap is a solid-color ellipse. Along-axis
  views show only the facing disk; exact side views omit the edge-on cap.
- Sphere: one circle uses a radial-gradient approximation. In camera coordinates,
  let `(sx, sy, sz)` be the unit direction toward the source and
  `l = sqrt(sx² + sy²)`. The normalized gradient center is
  `(0.5 + 0.35*sx, 0.5 + 0.35*sy)` and radius is `0.5 + 0.15*l`.
  Peak diffuse strength is 1 for `sz >= 0`, otherwise `l`. Between the bright
  center and ambient boundary, 33 stops sample `(1 + cos(pi*t))/2`, giving
  a smooth falloff. This is a visual approximation, **not pointwise Lambert
  lighting**. Direct backlight produces ambient-only color.

`light=None` produces intrinsic solid fills. SVG uses native `linearGradient`
and `radialGradient`; TikZ/PDF uses the existing functional-shading adapter with
identical stops, transforms and direct RGB interpolation. Curved boundaries use
cubic Bezier arcs; no raster fill, SVG lighting filter or gradient mesh is needed.
Spheres/cylinders sort atomically by their center depth, without interleaving their
surfaces with other objects. Intersection and cyclic-occlusion limits still apply.

Run `uv run python -m examples.spatial.curved_solids` to generate light-direction
comparisons and camera/axis checks in SVG, TikZ and PDF.

![Smooth curved solids](../examples/output/spatial/curved_solids.svg)

![Cylinder camera checks](../examples/output/spatial/curved_solids-views.svg)

```{literalinclude} ../examples/spatial/curved_solids.py
:language: python
```

## Polygon visibility and approximate modes

`Scene3D(visibility="auto")` uses BSP for scenes of Polyhedron objects without
face artwork. Simple concave loops are triangulated as necessary; crossing faces
and visibility cycles are split and painted far-to-near in both cameras. New cut
edges have no strokes. Opacity is ordinary per-fragment compositing, including
back faces; it does not create boolean solids or simulate refraction. Coplanar
ties use source object/face input order, with later faces on top.

`visibility="bsp"` explicitly requires this supported scene. Curved solids, free
Plane3D placements and face artwork raise an error. In auto these select centroid
ordering for the **entire scene**, with a warning. Specify `visibility="centroid"`
to acknowledge the approximation. Faces sort by vertex-average depth; curved
solids use centers, and planar drawings use their explicit depth reference. This
mode cannot generally resolve intersections or cycles. Separate scenes always
follow ordinary Canvas order.

`projected.visibility` reports `bsp`, `centroid` or `manual`.
`projected.source_faces` maps every child to its original `(object, face)` index,
or None for non-polyhedra. BSP can repeat a source face across several children;
source vertex and face-center queries retain original indices. `reordered()`
permutes the mapping too and marks the result manual. `sort_faces=False` bypasses
all sorting/splitting and preserves the original complete object/face order.

BSP uses an absolute finite positive `bsp_tolerance=1e-8` mm plane tolerance,
not exact predicates. `max_fragments=100000` includes triangulation; this budget
and an internal tree-depth limit of 500 raise ValueError on exhaustion, without
fallback. Supporting planes can split disjoint finite faces and increase output
size. Near-plane crossings still fail explicitly. Automatic hidden-edge dashes,
face-artwork clipping and analytic curved-surface visibility are not provided.

See [Intersections and visibility](tutorial/en/05-spatial/05-visibility.md) for runnable
examples and the 3D splitting → 2D Authoring flow.

## Perspective

`PerspectiveCamera` shares the orthographic angles and target. `distance=100`
places the eye along toward_viewer; `focal_length=100` controls image scale;
`near=0.1` rejects points too close to or behind the eye. All are millimeters,
finite and positive, with near < distance. Equal distance/focal_length preserve
scale on the target plane. Polyhedra and solid-filled path-compatible planar
artwork are supported; Sphere/Cylinder remain orthographic-only. Perspective
plane text becomes vector outlines in the later Canvas context; curves use
adaptive polylines with 0.02 mm local projection tolerance. Constant-width
strokes are retained. No near-plane cutting, gradients or embedded images on
perspective planes are supported. Add ordinary 2D legends after projection.

See [Perspective](tutorial/en/05-spatial/03-perspective.md) and
[Transparency and depth order](tutorial/en/05-spatial/04-depth-order.md) for runnable
comparisons, camera parameters, manual order and the exact scope limits.

## Smooth cylindrical patches and explicit projection layers

`CylinderSurface` adds an open angular side patch without caps or thickness;
`AnnularCylinder` adds a closed washer with inner/outer walls and annular caps.
Both use uniform color, independent of DirectionalLight, and require an
OrthographicCamera. They keep curved vector boundaries without a polygon mesh.
Use similarity transforms for 3D edits; shear/nonuniform scales are rejected.

See [Cylindrical surfaces](tutorial/en/05-spatial/06-curved-surfaces.md) for angles,
coordinate conventions, view checks and runnable examples. The
[material/probe recipe](tutorial/en/05-spatial/07-projected-composition.md) explains independent
Scene3D projections: share a camera/world frame and apply matching 2D placements,
then control coverage with ordinary Canvas order or layers. BSP and face splitting
are scoped to one project call. Independent snapshots never share visibility
state, even if their source scenes use the same camera.

The cutaway's interior floor is an explicit Plane3D drawing. It is an illustration,
not an automatic solid section. Curves remain outside BSP; auto mode warns and
uses centroid ordering, explicit BSP rejects them, and sort_faces=False chooses
manual object order. Visible parts within a single curved object still receive
its own internal drawing order.
