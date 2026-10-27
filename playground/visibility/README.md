# Polygon visibility playground

An independent prototype of BSP visibility for **opaque convex planar polygons**.
It does not change `Scene3D` or any public pdl API. Each source face has a stable
ID; fragments keep that ID. Output is an ordinary `ProjectedScene` containing
2D `Drawing` objects, before Canvas evaluation and backend rendering.

[中文说明](README_zh.md)

## Run

From the repository root:

```sh
uv run python -m playground.visibility.run --counts 32 96 256 --repeats 3 --samples 1024
uv run python -m pytest playground/visibility/test_bsp.py -q
uv run pyright playground/visibility
```

If uv's default cache is restricted, prefix commands with
`UV_CACHE_DIR=/private/tmp/pdl-uv-cache`.

The runner writes ignored artifacts under `playground/visibility/output/`:

- `comparison.svg`, `.tex`, `.pdf`: centroid-order reference and BSP results
  with identical geometry/colors and perspective cameras. Cases include a
  parallel-face ordering trap, intersecting planes, a three-ribbon visibility
  cycle, and a dense random scene. Only original boundaries receive strokes.
- `sparse-*.svg`, `medium-*.svg`, `dense-*.svg`: every benchmark scene, without
  labels or fonts inside the timed region.
- `timings.csv`, `results.json`: all repeat ranges, medians, original and fragment
  counts, split counts, tree depth, source seeds, platform and camera metadata.

PDF comparison export needs XeLaTeX. For a PNG preview, use an available PDF
rasterizer; e.g. `gs -q -dSAFER -dBATCH -dNOPAUSE -sDEVICE=png16m -r110
-sOutputFile=playground/visibility/output/comparison.png
playground/visibility/output/comparison.pdf` as one shell command.

## Algorithm and timing boundary

`bsp.py` selects a partition from up to seven candidate face planes, penalizing
splits and unbalanced subtrees. Each polygon is classified against the chosen
plane. Straddling polygons are clipped into two convex fragments; front and back
subsets are recursively partitioned. Eye-relative far/plane/near traversal yields
a valid painter order under nondegenerate exact geometry. This handles actual
intersections and cyclic occlusion without a centroid-depth ordering heuristic.
Infinite supporting planes can also split polygons that do not intersect the
finite partition polygon: this conservative over-splitting is deliberate.

New cut edges are tagged as non-boundary. Each fragment becomes a fill and its
remaining original boundary segments, so BSP cuts do not become black outlines.
Source geometry and colors are immutable. Coplanar overlapping faces use larger
source IDs on top, irrespective of winding. The source-query arrays in
`ProjectedScene` use **input tuple order**, with one face per input entry; the
returned fragments expose the actual `source` IDs.

`project()` times source near-plane checks and projected source-query metadata,
BSP construction, traversal, fragment projection, and 2D Authoring construction.
It returns before Canvas evaluation, text measurement, serialization, SVG export,
TeX compilation or independent visibility checking. No BSP or projection cache
is reused between repeats. The baseline times the existing
`Scene3D.project()` call; baseline source construction is also outside the clock.
Per-stage times are the last repeat; total min/median/max use all repeats.
`build_seconds` includes initial near-plane/source metadata work.

`scenes.py` uses seeded standard-library randomness. Centers lie in a fixed
100 mm cube; radii grow with the density parameter. Face normals are uniform on
the sphere. Shapes are affine-regular convex polygons with 3–7 vertices, randomized
aspect ratios and rotations. Count/seed pairs use the same random draws across
densities. Density therefore changes face sizes, not the random centers/normals.
The input is not a uniform sample of all possible convex polygons.

## Verification and limits

`oracle.py` independently compares the last painted fragment at sampled screen
points with the closest original face found by ray/plane intersection. Half the
rays cover the screen uniformly; half target source interiors to exercise sparse
scenes. This is a numerical sampled check, **not a proof of all-pixel correctness**.
Tests additionally check fragment area conservation, original perimeter retention,
plane-through-vertex splitting, coplanar policy, and failure paths. The cycle
regression checks that every whole-face permutation still has visibility errors.

- Only valid convex planar faces, solid opaque colors, two-sided fills and
  constant-width original boundary strokes. Input validity is a precondition;
  arbitrary user polygons are not comprehensively validated here.
- No concave faces, holes, curved surfaces, transparency, surface artwork,
  shadows, or boolean-solid construction.
- No near-plane clipping: source vertices at/before the near plane fail explicitly.
- Float arithmetic with an absolute `1e-8` mm plane tolerance, not exact predicates.
  Tolerance-sized gaps/ties may be treated as coplanar. Rescale extreme geometry.
- Safety budgets: 100,000 fragments and tree depth 500. Exceeding them raises an
  error; it never silently falls back to centroid sorting.
- BSP can cause substantial fragment growth. It has no projected-bound pruning,
  spatial index, plane cache or optimized numeric kernel yet.
- Raster viewers may show antialias seams between touching filled fragments;
  these are not stroked cut edges. No pixel-baseline comparison is provided.

See [RESULTS.md](RESULTS.md) for the measured local run and interpretation.

## Formal library implementation

The prototype is retained as a historical experiment. pdl now selects BSP in
`Scene3D.project()` for polygon-only scenes without face artwork, with concave
loop decomposition, source-face correspondence and explicit visibility modes.
Use `uv run python -m playground.visibility.library` to benchmark the public
library through 2D Authoring and check its actual paint list against the same
independent oracle. This writes `output/library-*.svg`, `library-results.json`
and `library-timings.csv`. The original runner explicitly requests centroid
mode for its baseline so upgrading pdl does not accidentally change the reference.
See the [formal tutorial](../../docs/tutorial/en/26-visibility.md).
