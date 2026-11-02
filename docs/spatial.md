# 3D components, projection, and visibility

Point3D, Vector3D, and Transform3D use right-handed millimeter coordinates.
Transforms return new solids. Polyhedron stores indexed vertices and ordered face
loops, with regular-solid constructors, concave loops, colors, and opacity.
Faces must be simple, planar, and nondegenerate. Plane3D carries 2D artwork on an
origin/basis chart; face_plane provides a chart for an indexed face.

Scene3D.project explicitly produces an editable 2D ProjectedScene Group for
Canvas. vertex/face_center/point return current projected numbers and follow
later 2D edits without modifying the source scene. Artwork retains native Text
under suitable similarities. TeX retains source under translation/rotation;
scaling or other deformation lowers measured outlines immediately.
Artwork is not automatically clipped or lit.

OrthographicCamera preserves millimeters. PerspectiveCamera uses a pinhole model
and rejects near-plane crossings without clipping. Plane curves and glyphs use
bounded-error path subdivision; images and curved solids require supported
orthographic workflows. DirectionalLight supplies simple face-color shading,
without shadows or physical light transport.

visibility="auto" selects BSP for polyhedra without artwork. It splits
intersections, retains source-face indices, and avoids stroking new cut edges.
Unsupported content uses a warned centroid fallback; explicit bsp rejects it,
and explicit centroid acknowledges approximate sorting. sort_faces=False keeps
input order. Floating tolerances, fragment budgets, and tree depth bound the
algorithm; solid booleans are outside its scope.

Sphere, Cylinder, CylinderSurface, and AnnularCylinder use smooth paths/gradients
for orthographic diagrams, with centroid/manual ordering and documented
similarity-transform restrictions. Separate projections combine through Canvas
order and share no BSP/depth buffer. Project components separately for deliberate
illustration coverage, keeping reference views beside the final assembly.


![All five Platonic solids](../examples/output/spatial/platonic_solids.svg)

![Plane placement](../examples/output/spatial/planes.svg)

![D10 face artwork and 2D legend](../examples/output/spatial/d10.svg)

![Smooth curved solids](../examples/output/spatial/curved_solids.svg)

![Cylinder camera checks](../examples/output/spatial/curved_solids-views.svg)

[3D tutorial](tutorial/en/05-spatial/index.md) · [API](api/extensions/spatial/index.md)
