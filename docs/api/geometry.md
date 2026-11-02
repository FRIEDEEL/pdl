# Geometry and drawing factories

The drawing factories return Entity. Import corresponding PascalCase pure descriptions from
`pdl.author.geometry` when constructing paths or querying numerical parameters.
A bare description cannot be submitted to Canvas. Import the path builder as
`from pdl.author.geometry import Path`; examples may alias it as PathGeometry
to distinguish filesystem paths. `Entity(builder)` or `path(builder)` attaches drawing behavior.

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

## line drawing factory

```{eval-rst}
.. autofunction:: pdl.line
```

## polyline drawing factory

```{eval-rst}
.. autofunction:: pdl.polyline
```

## polygon drawing factory

```{eval-rst}
.. autofunction:: pdl.polygon
```

## rectangle drawing factory

```{eval-rst}
.. autofunction:: pdl.rectangle
```

## circle drawing factory

```{eval-rst}
.. autofunction:: pdl.circle
```

## arc drawing factory

```{eval-rst}
.. autofunction:: pdl.arc
```

## path drawing factory

```{eval-rst}
.. autofunction:: pdl.path
```

## Point

```{eval-rst}
.. autoclass:: pdl.author.geometry.Point
   :members:
   :member-order: bysource
```

## Vector

```{eval-rst}
.. autoclass:: pdl.author.geometry.Vector
   :members:
   :member-order: bysource
```

## Pure Path

```{eval-rst}
.. autoclass:: pdl.author.geometry.Path
   :members:
   :member-order: bysource
```

## Bounds

```{eval-rst}
.. autoclass:: pdl.author.geometry.Bounds
   :members:
   :member-order: bysource
```

## Pure Line

```{eval-rst}
.. autoclass:: pdl.author.geometry.Line
   :members:
   :member-order: bysource
```

## Pure Polyline

```{eval-rst}
.. autoclass:: pdl.author.geometry.Polyline
   :members:
   :member-order: bysource
```

## Pure Polygon

```{eval-rst}
.. autoclass:: pdl.author.geometry.Polygon
   :members:
   :member-order: bysource
```

## Pure Rectangle

```{eval-rst}
.. autoclass:: pdl.author.geometry.Rectangle
   :members:
   :member-order: bysource
```

## Pure Circle

```{eval-rst}
.. autoclass:: pdl.author.geometry.Circle
   :members:
   :member-order: bysource
```

## Pure Arc

```{eval-rst}
.. autoclass:: pdl.author.geometry.Arc
   :members:
   :member-order: bysource
```

## Transform application

The mapping classes describe explicit coordinate maps. Matrix `apply` maps
pairs, `map` returns a Point, and `left @ right` applies right first. Applying a
matrix through `apply_transform`/`apply_to` uses that explicit world map. Entity
`rotate`, `scale`, and `rescale` select the reference pivot by default; use
`origin=` or a matrix's `around(...)` to make a pivot explicit.

Transforms immediately replace current geometry. Nonuniform circle scaling
lowers to a cubic Path. Uniform Rescale can explicitly include line width;
nonuniform Scaling leaves width unchanged. Matrix composition returns a plain
AffineTransform, so apply Rescale separately to retain its paint option.
Nonlinear/mesh algorithms remain
future work, and unsupported curve mappings are rejected.

### Transform

```{eval-rst}
.. autoclass:: pdl.author.transform.Transform
   :members:
   :member-order: bysource
```

### AffineTransform

```{eval-rst}
.. autoclass:: pdl.author.transform.AffineTransform
   :members:
   :member-order: bysource
```

### Translation

```{eval-rst}
.. autoclass:: pdl.author.transform.Translation
   :members:
   :member-order: bysource
```

### Rotation

```{eval-rst}
.. autoclass:: pdl.author.transform.Rotation
   :members:
   :member-order: bysource
```

### Scaling

```{eval-rst}
.. autoclass:: pdl.author.transform.Scaling
   :members:
   :member-order: bysource
```

### Rescale

```{eval-rst}
.. autoclass:: pdl.author.transform.Rescale
   :members:
   :member-order: bysource
```

### Shear

```{eval-rst}
.. autoclass:: pdl.author.transform.Shear
   :members:
   :member-order: bysource
```

### Reflection

```{eval-rst}
.. autoclass:: pdl.author.transform.Reflection
   :members:
   :member-order: bysource
```
