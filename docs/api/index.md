# API reference

Use this section to check a signature, default, unit, or behavior. For your
first drawing, follow the [tutorial](../tutorial/en/index.md) instead.
Import public objects from `pdl`; implementation module paths are not the
recommended user API.

本节给出公共接口的签名、默认值、单位和行为约定，接口说明直接来自英文 docstring。
中文入门说明见[教程](../tutorial/zh/index.md)。

- Coordinates and shape sizes use millimeters, with x right and y up.
- Text and TeX sizes use TeX points (1/72.27 inch).
- Numerical geometry is reusable; Entity methods modify the handle.
- Draw captures built-in mutable state. Measurements happen when queried or rendered.
- All interfaces are provisional before release. TikZ-style aliases are not yet implemented.

## Types used in signatures

| Name | Accepted values |
|---|---|
| `Position` | A `Point` or an `(x, y)` coordinate pair |
| `PointSource` | A Position, deferred `AnchorRef`, or frame-qualified `SpacePoint` |
| `Graphic` | Numerical geometry or a composite such as a Node, Group, or Entity |
| `Anchor` | `center`, `north`, `south`, `east`, `west`, or a spaced diagonal such as `north east` |
| `Self` | The same kind of object as the method's receiver; Entity/Path builder methods return the modified receiver |

These names explain type annotations; import the public classes from `pdl`.
Do not import internal aliases just to supply ordinary coordinates or objects.

```{toctree}
:maxdepth: 1

drawing
geometry
authoring
coordinates
flowcharts
text
```
