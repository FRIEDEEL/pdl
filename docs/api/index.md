# API reference

Drawing factories imported from `pdl` return Entity objects. Pure descriptions
live in `pdl.author.geometry`; use them for geometric construction and explicit
`Entity(geometry, style=...)` composition. There is no common Geometry base class.

Coordinates and line widths use millimeters, x right and y up. Text/TeX size uses
TeX points. Entity methods mutate and return the receiving object. Queries return
fixed numerical values. Canvas submission captures geometry, effective paint,
and typography independently of later edits.

| Name | Meaning |
| --- | --- |
| Position | Point or an `(x, y)` pair |
| Anchor | center, north, south, east, west, or a spaced diagonal |
| Entity | Current geometry, optional Style, reference point, and drawing operations |
| Group | Entity owning ordered members with style fallback |
| Gather | Explicit identity selection; no ownership or inherited paint |
| Frame | Explicit numerical origin and basis; visualized with frame_axes |

This reference is generated from English source docstrings. See the
[tutorial](../tutorial/en/index.md) for a step-by-step introduction.

```{toctree}
:maxdepth: 1

drawing
geometry
authoring
coordinates
flowcharts
spatial
text
```
