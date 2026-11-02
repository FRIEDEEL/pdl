# pdl.author.geometry.frame

Frame stores a current origin and basis. Ordinary Entities use world coordinates
and have no implicit frame. `CoordinateSystem` is an alias of Frame. A Frame is
not submitted directly; frame_axes creates a drawable Entity Group.

Source: `src/pdl/author/geometry/frame.py`.

```{eval-rst}
.. automodule:: pdl.author.geometry.frame
   :members: Frame, WORLD, CoordinateSystem, SpacePoint, SpaceVector
   :undoc-members:
   :ignore-module-all:
   :member-order: bysource
```
