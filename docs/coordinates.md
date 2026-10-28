# Authoring state, coordinates, and numerical queries

Concrete shapes, Text, TeX, Image and Group are editable Author objects.
Their parameters describe local content; placement applies affine transforms.
There is no separate Resolved drawing model.

## Immediate values and capture

`object.anchor(name)` immediately returns a numerical world-space Point of the
current object state. Text anchors can invoke font or TeX measurement. Later
edits never update the returned point. `move_to` / `place` immediately position
the transformed bounds center at the supplied world point. Use explicit frame
points for local coordinates. Path.move_to builds a subpath; Path.place moves
the complete path. Default rotation/scaling pivots are measured immediately.

```python
from pdl import Canvas, Circle, Rectangle

a = Rectangle((0, 0), 20, 10)
b = Circle((0, 0), 2).place(a.anchor("east"))
a.translate(30, 0)  # b retains its previously calculated position
canvas = Canvas(100, 60)
canvas.draw(b)
canvas.draw(a)  # paint order is independent of the earlier calculation
```

`with measurement(RendererConfig(...)):` or `with canvas.typography():` selects
fonts and TeX configuration before querying. Ordinary Text can discover default
fonts when unspecified. TeX uses its explicit configuration or the current default.
Construction alone does not measure; queries, measured placement and submission do.

`Canvas.draw` captures state and typography with canvas settings. Changes to
objects, fonts or per-render settings do not relayout existing submissions.
`Canvas.snapshot` returns the same kind of ordinary captured Drawing without
submitting it, in authoring coordinates. There are no deferred anchor references.

## Coordinate spaces

Coordinates are Cartesian millimeters, x right and y up. CoordinateSystem holds
an explicit immutable affine frame; point and vector references can be converted
numerically. `in_space(frame)` places local geometry in that frame. An Entity's
space captures its current placed coordinates; its separate frame reference does
not follow transforms. These accessors remain provisional in this first refactor.

`canvas.map(frame, matrix)` affects subsequent canvas measurements/submissions;
it does not rewrite already captured records. `canvas.map(WORLD, matrix)` applies
the final page-wide base mapping, including existing records. Matrix composition
uses rightmost-first order. Singular inverse conversions raise ValueError.

An ordinary shape's east anchor is its local anchor transformed into world space;
a Group anchor uses its visible world axis-aligned bounds. Use `anchor + vector.resolve()`
for a numerical frame-qualified offset. Translation affects points, not vectors.

## Queries and viewport

- `query().point(...)` and `query().vector(...)` return final canvas values.
- `query().bounds(...)` returns geometry/layout bounds excluding stroke.
- `query().ink_bounds(...)` measures glyph outlines rather than layout boxes.
- `in_space=frame` selects authoring coordinates before final viewport adaptation.
- `query().from_canvas(...)` converts a numerical canvas point back to authoring coordinates.

Queries never draw their targets. The paint list determines fit/auto-size; with
an empty list, a bounds query uses its target for fitting, while a point query
uses only the base mapping. Query final page coordinates after submitting content.

Clip uses a fixed viewport; fit scales uniformly into a fixed viewport; auto_size
preserves author scale and derives dimensions. Fitting includes conservative
stroke margins, not exact painted bounds. Glyphs transform with geometry;
stroke widths remain final canvas millimeters. Empty bounds have no anchor.

Backends encode captured shapes and positioned text. Native glyph shaping can
still differ between SVG viewers and TeX. Exact stroke bounds, nonlinear frames,
automatic routing and general constraint solving remain outside this model.
