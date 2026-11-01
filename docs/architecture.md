# Source architecture

## Current refactor boundary

The previous implementation and tests now live in `src/pdl_old` and `tests_old`.
The new `src/pdl` package is rebuilt incrementally. Its agreed Author structure is:

| Package | Owns | May depend on |
| --- | --- | --- |
| `author.geometry` | Independent geometric descriptions and their numerical queries | Standard library, transform, and util when needed |
| `author.style` | Style descriptions | Standard library and util when needed |
| `author.entity` | Drawing instances, object relationships, and user operations | Geometry, style, transform, and util |
| `author.transform` | General spatial-mapping contract and concrete affine matrices | Standard library and util; no other pdl domain package |
| `author.util` | Pure numerical functions and external font/TeX interfaces | Standard library, external libraries and tools; no other pdl layer |

The first implemented geometry modules are `point.py` and `path.py`. Point is an
immutable finite coordinate value. Path is a mutable builder with immutable
command snapshots. Neither inherits a common Geometry base or depends on Entity,
styles, output adapters, or the old package. Ordinary coordinates default to the
authoring world; no implicit local frame is attached. Geometry mutation policies
are defined per type rather than imposed by a common base.

Use the explicit module imports during this checkpoint:

```python
from pdl.author.geometry.point import Point
from pdl.author.geometry.path import Path
```

`author.transform` is a sibling of geometry and entity, not a geometry subpackage.
`Transform` declares only numerical coordinate-pair mapping, without a required
matrix, inverse, or object dispatch. `AffineTransform` stores a finite affine
matrix. Its user-facing subclasses are `Translation`, `Rotation`, `Scaling`,
`Shear`, and `Reflection`. All are immutable matrix values. `left @ right`
applies right first and returns a general AffineTransform; inverse is available
only on affine types and rejects singular matrices. `around((x, y))` supplies an
explicit pivot without consulting object reference points.

```python
from pdl.author.transform.affine import Rotation, Translation

mapping = Translation(10, 0) @ Rotation(90)
coordinates = mapping.apply((1, 0))  # Approximately (10, 1).
```

The transform package does not import Point, Path, Entity, or Style. Geometry and
Entity adapt their data to numerical coordinate pairs and define their own
supported application behavior. Path transformation, reference-point queries,
bounds, typography, Canvas, and backends have not yet been rebuilt.
Nonlinear/mesh mappings and their composition or path approximation are deferred.

`author.style.color.Color` is an immutable RGB value with channels in [0, 1].
`author.style.style.Style` describes solid fill/stroke, line width in millimeters,
line caps/joins, fill rule, and opacity. It is a complete immutable value, without
geometry, object ownership, output encoding, or default/inheritance resolution.
Within a Style, None disables the corresponding fill or stroke; an Entity's
`style=None` has a separate meaning of using its type default. Group fallback
remains deferred.
Style's own constructor defaults to a black 1 mm outline and no fill; Entity
types are not required to use those defaults. Gradients, typography attributes,
and Group compositing are not implemented in this step.

```python
from pdl.author.style.color import Color
from pdl.author.style.style import Style

paint = Style(stroke=None, fill=Color(0.2, 0.4, 0.8), opacity=0.75)
```

`author.entity.base.Entity[GeometryT]` directly retains its constructor's geometry
and optional explicit Style. There is no implicit copy, ownership registry,
common Geometry base, or geometry conversion. Concrete drawing constructors
should normally create their own geometry. Explicitly passing the same mutable
description to multiple instances intentionally shares geometry edits; callers
can pass `geometry.copy()` when independent descriptions are required.

`style` preserves None for an unset instance. `effective_style` reads the explicit
value or current class-level `default_style` without writing the default back.
Subclasses may override their class default. `set_style(style)` changes only the
receiving instance and returns it, even when geometry is shared. Resetting with
None, Entity copying, transform storage/application, anchors, Group/Gather,
capture, and rendering remain outside this minimal checkpoint.

```python
from pdl.author.entity.base import Entity

description = Path().move_to((0, 0)).line_to((10, 0))
instance = Entity(description, style=paint)
assert instance.geometry is description
```

Tests mirror geometry, transform, style, and entity under `tests/unit/author/`.
Do not import `pdl_old` to fill these gaps. Agreed
design and remaining questions are recorded in the temporary `refactor_note.md`.

## Legacy architecture (reference only)

The remaining sections describe the pre-refactor implementation under
`src/pdl_old`. They are historical reference, not implemented APIs or placement
contracts of the new `pdl` package.

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
