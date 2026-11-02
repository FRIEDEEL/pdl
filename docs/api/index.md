# API reference — pdl

The reference follows the packages and modules under `src/pdl/`. Choose a package below, then open a module for its classes, functions, signatures, and source docstrings.

Lengths and line widths use millimeters; text and TeX sizes use TeX points. Entity edits take effect immediately, position queries return fixed values, and Canvas captures submissions independently of subsequent edits.

The reference is maintained in English. [Start with the tutorial](../tutorial/en/index.md) for guided examples.

Source: `src/pdl/__init__.py`.

```{eval-rst}
.. automodule:: pdl
```

## Packages and modules

```{toctree}
:maxdepth: 1

author/index
backends/index
canvas/index
extensions/index
```

## Re-exported names

These imports link to their defining modules. Full member documentation is kept at the definition rather than repeated here.

| Import | Defined in |
| --- | --- |
| `pdl.AffineTransform` | {py:obj}`pdl.author.transform.affine.AffineTransform` |
| `pdl.AnnularCylinder` | {py:obj}`pdl.extensions.spatial.surfaces.AnnularCylinder` |
| `pdl.BLACK` | {py:obj}`pdl.author.style.color.BLACK` |
| `pdl.Bounds` | {py:obj}`pdl.author.geometry.bounds.Bounds` |
| `pdl.Canvas` | {py:obj}`pdl.canvas.canvas.Canvas` |
| `pdl.Color` | {py:obj}`pdl.author.style.color.Color` |
| `pdl.ColorStop` | {py:obj}`pdl.author.style.gradient.ColorStop` |
| `pdl.Connection` | {py:obj}`pdl.extensions.diagram.connections.Connection` |
| `pdl.CoordinateSystem` | {py:obj}`pdl.author.geometry.frame.CoordinateSystem` |
| `pdl.CoordinateSystem3D` | {py:obj}`pdl.extensions.spatial.coordinates.CoordinateSystem3D` |
| `pdl.Cylinder` | {py:obj}`pdl.extensions.spatial.curves.Cylinder` |
| `pdl.CylinderSurface` | {py:obj}`pdl.extensions.spatial.surfaces.CylinderSurface` |
| `pdl.Decision` | {py:obj}`pdl.extensions.diagram.flowchart.Decision` |
| `pdl.DirectionalLight` | {py:obj}`pdl.extensions.spatial.projection.DirectionalLight` |
| `pdl.Entity` | {py:obj}`pdl.author.entity.base.Entity` |
| `pdl.FlowEdge` | {py:obj}`pdl.extensions.diagram.flowchart.FlowEdge` |
| `pdl.FlowNode` | {py:obj}`pdl.extensions.diagram.flowchart.FlowNode` |
| `pdl.Font` | {py:obj}`pdl.author.style.font.Font` |
| `pdl.FontStack` | {py:obj}`pdl.author.style.font.FontStack` |
| `pdl.Frame` | {py:obj}`pdl.author.geometry.frame.Frame` |
| `pdl.Gather` | {py:obj}`pdl.author.entity.gather.Gather` |
| `pdl.Group` | {py:obj}`pdl.author.entity.group.Group` |
| `pdl.Layer` | {py:obj}`pdl.canvas.layers.Layer` |
| `pdl.LayerStack` | {py:obj}`pdl.canvas.layers.LayerStack` |
| `pdl.LinearGradient` | {py:obj}`pdl.author.style.gradient.LinearGradient` |
| `pdl.Node` | {py:obj}`pdl.extensions.diagram.nodes.Node` |
| `pdl.OrthographicCamera` | {py:obj}`pdl.extensions.spatial.projection.OrthographicCamera` |
| `pdl.PathGeometry` | {py:obj}`pdl.author.geometry.path.Path` |
| `pdl.PerspectiveCamera` | {py:obj}`pdl.extensions.spatial.projection.PerspectiveCamera` |
| `pdl.Plane3D` | {py:obj}`pdl.extensions.spatial.solids.Plane3D` |
| `pdl.Point` | {py:obj}`pdl.author.geometry.point.Point` |
| `pdl.Point3D` | {py:obj}`pdl.extensions.spatial.coordinates.Point3D` |
| `pdl.Polyhedron` | {py:obj}`pdl.extensions.spatial.solids.Polyhedron` |
| `pdl.Position` | {py:obj}`pdl.author.geometry.point.Position` |
| `pdl.ProjectedScene` | {py:obj}`pdl.extensions.spatial.projected.ProjectedScene` |
| `pdl.Query` | {py:obj}`pdl.canvas.query.Query` |
| `pdl.RadialGradient` | {py:obj}`pdl.author.style.gradient.RadialGradient` |
| `pdl.Reflection` | {py:obj}`pdl.author.transform.affine.Reflection` |
| `pdl.RendererConfig` | {py:obj}`pdl.author.style.typography.RendererConfig` |
| `pdl.Rescale` | {py:obj}`pdl.author.transform.affine.Rescale` |
| `pdl.Rotation` | {py:obj}`pdl.author.transform.affine.Rotation` |
| `pdl.Scaling` | {py:obj}`pdl.author.transform.affine.Scaling` |
| `pdl.Scene3D` | {py:obj}`pdl.extensions.spatial.projection.Scene3D` |
| `pdl.Shear` | {py:obj}`pdl.author.transform.affine.Shear` |
| `pdl.SpacePoint` | {py:obj}`pdl.author.geometry.frame.SpacePoint` |
| `pdl.SpaceVector` | {py:obj}`pdl.author.geometry.frame.SpaceVector` |
| `pdl.Sphere` | {py:obj}`pdl.extensions.spatial.curves.Sphere` |
| `pdl.Style` | {py:obj}`pdl.author.style.style.Style` |
| `pdl.Surface3D` | {py:obj}`pdl.extensions.spatial.solids.Surface3D` |
| `pdl.TeXConfig` | {py:obj}`pdl.author.util.tex.TeXConfig` |
| `pdl.Terminal` | {py:obj}`pdl.extensions.diagram.flowchart.Terminal` |
| `pdl.Transform` | {py:obj}`pdl.author.transform.base.Transform` |
| `pdl.Transform3D` | {py:obj}`pdl.extensions.spatial.coordinates.Transform3D` |
| `pdl.Translation` | {py:obj}`pdl.author.transform.affine.Translation` |
| `pdl.Vector` | {py:obj}`pdl.author.geometry.point.Vector` |
| `pdl.Vector3D` | {py:obj}`pdl.extensions.spatial.coordinates.Vector3D` |
| `pdl.WORLD` | {py:obj}`pdl.author.geometry.frame.WORLD` |
| `pdl.arc` | {py:obj}`pdl.author.entity.factories.arc` |
| `pdl.circle` | {py:obj}`pdl.author.entity.factories.circle` |
| `pdl.frame_axes` | {py:obj}`pdl.author.entity.factories.frame_axes` |
| `pdl.image` | {py:obj}`pdl.author.entity.factories.image` |
| `pdl.line` | {py:obj}`pdl.author.entity.factories.line` |
| `pdl.measurement` | {py:obj}`pdl.author.style.typography.measurement` |
| `pdl.path` | {py:obj}`pdl.author.entity.factories.path` |
| `pdl.polygon` | {py:obj}`pdl.author.entity.factories.polygon` |
| `pdl.polyline` | {py:obj}`pdl.author.entity.factories.polyline` |
| `pdl.rectangle` | {py:obj}`pdl.author.entity.factories.rectangle` |
| `pdl.regular_polyhedron` | {py:obj}`pdl.extensions.spatial.solids.regular_polyhedron` |
| `pdl.tex` | {py:obj}`pdl.author.entity.factories.tex` |
| `pdl.text` | {py:obj}`pdl.author.entity.factories.text` |
