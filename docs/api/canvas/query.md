# pdl.canvas.query

Canvas queries default to final page coordinates. `in_space=WORLD` selects Author
world values; another explicit Frame requests its inverse conversion. WORLD
mapping and viewport fitting are final page policies. Query-frame overrides apply
to explicit SpacePoint/SpaceVector queries and leave already numerical geometry
unchanged.

Source: `src/pdl/canvas/query.py`.

```{eval-rst}
.. automodule:: pdl.canvas.query
   :members: Query
   :undoc-members:
   :ignore-module-all:
   :member-order: bysource
```
