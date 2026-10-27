# 22. Put artwork in a plane

A plane carries a local 2D drawing into 3D. Compare the same panel and native text
before and after tilting the plane. The letters change shape along with the panel;
they are not billboard labels facing the reader.

```{literalinclude} ../../../examples/tutorial/spatial/plane_text.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![Native text on flat and inclined planes](../../../examples/output/tutorial/spatial/plane_text.svg)

[Complete runnable example](../../../examples/tutorial/spatial/plane_text.py)

`Plane3D()` starts at the world origin with u along +x and v along +y. A local
point `(x, y)` means `origin + x*u + y*v`, in millimeters. The independent basis
vectors may also encode scaling or shear. `transformed()` returns a new plane.
The right-hand rotations first tilt around +x, then turn around +z, because the
rightmost matrix acts first. The top-down camera makes the untransformed chart
face the reader directly.

`plane.place(artwork)` describes a finite drawing in that infinite plane. It does
not draw the plane itself, clip the artwork or recolor it under the scene light.
The projected affine matrix affects panel geometry, text baseline and glyph shapes.
SVG uses the full matrix; native TikZ uses `transform shape`. No glyph-outline
conversion or raster texture is required. Text centering through Node is measured
later, in local 2D coordinates, before the plane transform is applied.

The bottom captions are added after projection and stay face-on. The artwork's
Node suppresses its box with `Style(stroke=None)`, retaining centered text only.
Keep artwork within the intended boundary yourself; clipping is not provided.
When a plane is exactly edge-on, its chart collapses; native text is omitted rather
than expanded into readable face-on labels. For perspective mapping and vector text outlines, continue to
[chapter 24](24-perspective.md).

Try changing the tilt from 55 to 20 degrees. The chart becomes less compressed,
while its independently drawn caption keeps the same shape.

[Previous: Project 3D](21-project-3d.md) · [Next: D10 face numbers](23-d10.md)
