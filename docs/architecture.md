# Source architecture

Author is the sole drawing object model. A measurement is an operation, not a
second scene representation. Anchors return fixed numerical points; later edits
to the queried object do not change previous results. Font and TeX measurement
can run during authoring, independently of drawing or output order.

## Responsibilities

| Package | Owns | May depend on |
| --- | --- | --- |
| `foundation.geometry` | Numerical points, vectors, paths, matrices and bounds algorithms | Standard library |
| `foundation.typography` | Font resources, shaping, TeX measurement, outlines and measurement configuration | Foundation and external font/TeX tools |
| `author` | Editable 2D shapes, Text/TeX/Image objects, composition, references, styles and layer identities | Foundation and Author |
| `canvas` | Captured submissions, layer ordering, queries, viewport and export entrypoints | Author, foundation and backend entrypoints |
| `backends` | SVG/TikZ encoding, native primitive selection, output fallback and PDF compilation | Author, foundation and the `canvas.records.Page` contract |
| `extensions.diagrams` | Nodes, connections and growing flowcharts | Author, foundation and extensions |
| `extensions.spatial` | 3D geometry, cameras, projection and visibility | Author, foundation and extensions |

Arrows below mean imports/calls, not drawing data flow:

```text
extensions ──→ author ──→ foundation
     └─────────────────→ foundation
canvas ──→ author / foundation / backend entrypoints
backends ──→ author / foundation / canvas.records.Page
```

`Page` is a small read-only protocol: dimensions and ordered Drawing records.
Backends never import the Canvas implementation. Author layer identities use a
small ordering protocol; the actual LayerStack lives in Canvas. These narrow
contracts avoid a dependency on the owning implementation.

The root `pdl` module is a lazy public facade. `from pdl import Canvas, Circle`
does not load 3D or diagram extensions. `pdl.author` is a core-only entrypoint.

## Author internals

- `entity.py`: common mutable operations and ownership access.
- `shapes.py`, `text.py`, `tex.py`, `image.py`: actual drawable objects.
- `composition.py`: Drawing records, editable Group and ordered group descriptions.
- `placement.py`: internal numerical placement state; it stores no deferred target.
- `measurement.py`: immediate queries and temporary per-operation caches.
- `capture.py`: state isolation and submission capture, using ordinary Author objects.
- `style.py`, `layers.py`, `gather.py`, `frames.py`, `spaces.py`: their respective
  styles, identities, selections and coordinate/reference operations.
- `references.py`: numerical position input types and transient internal anchor queries.

There are no `ResolvedGraphic`, `MeasuredText` or `MeasuredTeX` object families.
Captured text stores measured layout on the same Text/TeX type. A captured
Group description is an Author composition record, not a separate scene model.

## Timing and output

1. Construct and edit Author objects. Querying an anchor, moving an object by
   its measured center, or choosing a default rotation pivot can measure text.
2. A query returns numbers using the current state and measurement settings.
   Use `with measurement(RendererConfig(...)):` or `canvas.typography()` to
   select settings explicitly. Otherwise ordinary text discovers default fonts.
3. `Canvas.draw` captures geometry, placement and measured typography using the
   canvas settings. Extensions are decomposed to core 2D descriptions here.
4. The final paint list determines fit/auto-size. Backends encode that content;
   they do not recompute anchor relationships or revisit extension definitions.

`Canvas.snapshot` captures an ordinary Drawing without submitting it. Coordinates
remain in Author space; a destination Canvas applies its own final viewport.
`Canvas.resolve`, `ResolvedGraphic` and public deferred `AnchorRef` are removed.
Native TikZ node layout is removed: diagrams export fixed shapes and separately
positioned text. Backend-native glyph shaping can still differ from measurements;
fixed layout does not guarantee pixel-identical SVG and TeX text.

Explicit coordinate systems and the existing Entity frame/space accessors remain
provisional Author features in this first refactor. Their further simplification
is separate from this package-boundary change. Per-frame Canvas mappings affect
subsequent measurements/submissions, not already captured records. WORLD mapping
and fit are final page transforms.

## Enforced boundaries

`tests/architecture/test_boundaries.py` checks imports, including function-local
and type-only imports, and tests fresh-process imports of foundation and 2D core.
Behavior tests cover immediate anchor values, independent paint order, fixed draw
records, copying and regrouping, typography, diagrams, and 3D projections.

[中文说明](architecture_zh.md)
