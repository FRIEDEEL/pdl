# pdl.author.entity.factories

The drawing factories return Entity. Import corresponding PascalCase pure descriptions from
`pdl.author.geometry` when constructing paths or querying numerical parameters.
A bare description cannot be submitted to Canvas. PathGeometry is the public
path builder; `Entity(builder)` or `path(builder)` attaches drawing behavior.

| Default reference | Description |
| --- | --- |
| Circle / Arc | Center |
| Rectangle | Lower-left origin |
| Line / Polyline / Polygon | First point |
| PathGeometry | First Move, or (0, 0) while empty |
| Text / TeX | Baseline position |
| Group | Explicit reference, default (0, 0) |

Entity transforms preserve its reference even when the held geometry changes
representation. Bounds/anchors exclude stroke and use current world axes.

Source: `src/pdl/author/entity/factories.py`.

```{eval-rst}
.. automodule:: pdl.author.entity.factories
   :members: circle, line, polyline, polygon, rectangle, arc, path, text, tex, image, frame_axes, as_entity
   :undoc-members:
   :ignore-module-all:
   :member-order: bysource
```
