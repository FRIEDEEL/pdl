# Changelog

## Unreleased

### Changed

- **Breaking:** drawing constructors such as `circle` and `text` are factory functions
  returning thin Entity objects. Pure descriptions live in author.geometry;
  explicit Entity(geometry, style=...) construction is supported.
- **Breaking:** factory names are lowercase (`Circle` → `circle`, `TeX` → `tex`,
  and likewise for the other drawing factories). Actual classes retain PascalCase.
- **Breaking:** transforms immediately update current geometry. Stretching circles
  or native text can replace their representation with paths. There is no stored
  placement/accumulated matrix. Native text retains baseline, size, and orientation
  under supported similarity transforms. TeX translation/rotation retain source,
  while geometric scaling outlines measured artwork so absolute dimensions scale.
- **Breaking:** default pivots use reference points. Use origin= for an explicit
  pivot; set_reference changes the default. Queries use world-aligned logical
  bounds and fixed numerical positions.
- **Breaking:** Group uses varargs members, single-parent ownership, current world
  coordinates, and dynamic whole-style fallback. set_style updates only the Group.
  Gather operates on explicit Entity selections; use *group.members to edit members.
- **Breaking:** Frame is pure explicit geometry. Use frame_axes for drawable axes;
  ordinary objects no longer expose implicit frame/space. Layer belongs to Canvas.
- Canvas snapshots/submissions use ordinary Entities and fixed typography/paint.
  Drawing, placement wrappers, a common Geometry base, and foundation imports are
  removed from the new API. Use Entity.copy/apply_transform and author subpackages.
- Uniform Rescale optionally scales line width; nonuniform Scaling leaves it fixed.
- Existing font/TeX measurement, SVG/TikZ/PDF, images, gradients, diagrams, 3D
  projection, smooth surfaces, perspective artwork, and BSP visibility are migrated.
- Documentation and runnable examples are updated together while retaining their
  broad directory structure. The old implementation/tests remain archived for review
  and are excluded from built distributions.

### Migration examples

```python
from pdl import Entity, Group, PathGeometry, Rescale, Style, circle
from pdl.author.geometry import Arc as ArcGeometry

shape = circle((10, 10), 3, style=Style(line_width=0.5))
changed = shape.copy().scale(2, 1)
Rescale(2, include_linewidth=True).around(shape.reference).apply_to(shape)
path = Entity(PathGeometry().move_to((0, 0)).line_to((5, 2)))
arc = Entity(ArcGeometry.from_tikz((8, 4), radius=2, start_angle=0, end_angle=90))
group = Group(shape, path, arc)
```
