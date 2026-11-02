# pdl.author.transform

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

Source: `src/pdl/author/transform/__init__.py`.

```{eval-rst}
.. automodule:: pdl.author.transform
```

## Packages and modules

```{toctree}
:maxdepth: 1

affine
base
operations
```

## Re-exported names

These imports link to their defining modules. Full member documentation is kept at the definition rather than repeated here.

| Import | Defined in |
| --- | --- |
| `pdl.author.transform.AffineTransform` | {py:obj}`pdl.author.transform.affine.AffineTransform` |
| `pdl.author.transform.Reflection` | {py:obj}`pdl.author.transform.affine.Reflection` |
| `pdl.author.transform.Rescale` | {py:obj}`pdl.author.transform.affine.Rescale` |
| `pdl.author.transform.Rotation` | {py:obj}`pdl.author.transform.affine.Rotation` |
| `pdl.author.transform.Scaling` | {py:obj}`pdl.author.transform.affine.Scaling` |
| `pdl.author.transform.Shear` | {py:obj}`pdl.author.transform.affine.Shear` |
| `pdl.author.transform.Transform` | {py:obj}`pdl.author.transform.base.Transform` |
| `pdl.author.transform.Translation` | {py:obj}`pdl.author.transform.affine.Translation` |
