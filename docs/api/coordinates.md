# Explicit frames and numerical queries

Frame stores a current origin and basis. Ordinary Entities use world coordinates
and have no implicit frame. `CoordinateSystem` is an alias of Frame. A Frame is
not submitted directly; frame_axes creates a drawable Entity Group.

Canvas queries default to final page coordinates. `in_space=WORLD` selects Author
world values; another explicit Frame requests its inverse conversion. WORLD
mapping and viewport fitting are final page policies. Query-frame overrides apply
to explicit SpacePoint/SpaceVector queries and leave already numerical geometry
unchanged.

## Frame

```{eval-rst}
.. autoclass:: pdl.author.geometry.Frame
   :members:
   :member-order: bysource
```

## SpacePoint

```{eval-rst}
.. autoclass:: pdl.author.geometry.SpacePoint
   :members:
   :member-order: bysource
```

## SpaceVector

```{eval-rst}
.. autoclass:: pdl.author.geometry.SpaceVector
   :members:
   :member-order: bysource
```

## Query

```{eval-rst}
.. autoclass:: pdl.canvas.Query
   :members:
   :member-order: bysource
```

## Frame visualization

```{eval-rst}
.. autofunction:: pdl.frame_axes
```

```{eval-rst}
.. autoclass:: pdl.author.entity.frames.FrameAxes
   :members:
   :member-order: bysource
```

## WORLD

```{eval-rst}
.. autodata:: pdl.author.geometry.WORLD
   :no-value:
```
