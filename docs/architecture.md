# Source architecture

Author is the sole editable drawing domain. Geometry describes current shape
parameters, Style describes paint, and Entity combines them with numerical
position queries. Drawing factories such as Circle return Entity; pure shapes
are imported from author.geometry. No shared Geometry base is required.

## Responsibilities and dependencies

| Package | Owns | Dependency boundary |
| --- | --- | --- |
| author.geometry | Points, paths, shapes, explicit frames, native text/TeX/image descriptions, and numerical queries | Numeric affine mappings, utility services, and font resource/configuration modules; no Entity, Canvas, or renderer |
| author.style | Immutable paints, gradients, font descriptors, resource policy | Utilities and external resource discovery; no geometry ownership |
| author.transform.base / affine | Mapping contract and finite affine matrices | Numeric data and Point/Vector adapters |
| author.transform.operations | Immediate shape conversion and explicit paint changes | Geometry and Style; no concrete Entity dependency |
| author.entity | Thin instances, drawing factories, Group ownership, Gather selections, positioning, capture | Geometry, Style, Transform, and utilities; no Canvas or backend imports |
| author.util | Reusable infrastructure and explicit external-tool interfaces | Standard library, third-party libraries, external tools; no pdl imports |
| canvas | Submissions, layers, queries, viewport, and export entrypoints | Author and adapter entrypoints |
| backends | SVG/TikZ encoding and final PDF compilation | Current Author Entities and canvas.records.Page; no Canvas implementation |
| extensions.diagram / extensions.spacial | Parametric diagrams, 3D geometry, cameras, visibility | Core Author and their own components; no output adapters |

The existing spacial directory spelling is retained. Shape descriptors may use
numeric affine classes; application policy in transform.operations may inspect
shape types. This is a split between numerical mapping and conversion policy,
with no runtime module cycle. Utilities return ordinary measurements, raw font
outline commands, or tool results; they do not manage drawing relationships.
The root facade loads optional extensions lazily. Core-only imports do not load
diagrams or 3D. No pdl_old import is used to supply missing behavior.

## Current geometry and immediate edits

An Entity directly retains supplied geometry. Explicit mutable geometry sharing
is possible; direct shared edits are visible to both holders. A Transform
constructs the target's current result and replaces its geometry. Entity identity
remains stable when Circle becomes Path. No operation queue, accumulated object
matrix, or implicit local frame is retained. Entity.copy isolates geometry and
members and detaches the copied root from parent/layer identity.

Entity reference points determine default rotation/scaling pivots. Center and
world-aligned bounds anchors are separate queries. A matrix applied explicitly
uses its world mapping; around supplies a pivot. Curve mappings currently require
affine support. Nonlinear algorithms and approximation policies remain deferred.
Stroke width is unchanged by default. Uniform Rescale can explicitly include
line width; nonuniform scaling cannot use that option. Gradient coordinates can
be baked into current paint data to follow geometry.

Text/TeX store baseline position, size, and current orientation. Text retains
native form under orientation-preserving similarities. TeX retains native form
under translation/rotation; geometric scaling lowers its measured artwork to
paths, because changing font size would not scale absolute TeX dimensions.
Stretch/shear/reflection also lower text to paths. Conversion is irreversible on
that Entity. Unsupported rich SVG outline conversion fails explicitly, including
when viewport fitting requires scaling. Image geometry stores current viewport
corners and immutable source bytes; output matrices are derived for encoding.

## Ownership and paint

Group is an Entity with single-parent members in current world coordinates.
Transforms edit existing members together. Adding later does not replay past
edits. Member Style None remains None on entry and exit. Effective paint uses
explicit member Style, nearest explicitly styled ancestor, then the member's
own default. group.set_style changes only the Group. Gather is an identity
selection without ownership; its style operations target exactly selected
objects. Overlapping Group/member transform targets are processed once.

Capture preserves unset member styles. It freezes each object's own default and
clones the Group hierarchy, so captured Groups can still change their inherited
paint and removed members fall back to their captured defaults.

Layer belongs to Canvas. A Group occupies one effective layer, and captured
members paint contiguously. Layers can be reordered independently of geometry.
An explicit Frame is pure geometry; frame_axes creates a drawing Group whose
current basis and visual axes are edited together. Ordinary objects have no
implicit frame/space attributes.

## Query, capture, and output timing

1. Construct and edit Author objects. Queries return fixed numbers; references
   never establish live bindings or determine paint order.
2. Font/TeX measurement runs when an operation needs layout or outlines. Resource
   policy is shared by queries and submission through RendererConfig/typography.
3. Canvas.snapshot captures an ordinary Entity. Canvas.add/draw additionally
   records order and layer identity. Effective styles, font candidates, and
   typography are fixed on captured copies. Extensions expand into core Entities.
4. Viewport policy determines page dimensions and current output geometry.
   Backends consume the Page contract and encode Entity geometry/Style. No
   parallel Resolved scene hierarchy or TikZ-driven diagram layout is introduced.

Native SVG and LaTeX text can rasterize differently. Glyph resources are not
embedded into native SVG. TeX measurement cache keys include declared dependencies
and tool versions; undeclared environment changes require explicit invalidation.

## Verification and migration

Architecture tests enforce import boundaries, explicit imports, core-only
loading, and capture into ordinary Entity Groups. Numerical tests distinguish
shape/visibility algorithms from rendering. Integration tests compile real TeX,
PDF, gradients, fonts, and portable image assets.

The archived src/pdl_old and tests_old remain for review, outside active checks
and distribution artifacts. Current tests target the new semantics. Examples and
both language manuals use the new API. The implementation branch is followed by
a docs branch; merging into dev waits for explicit user review and approval.

[中文说明](architecture_zh.md)
