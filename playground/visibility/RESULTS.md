# Local performance snapshot

Measured on 2026-10-28 (Asia/Tokyo).

Environment: Python 3.12.13; `macOS-15.7.7-arm64-arm-64bit`.
CPU model was not available through the sandbox. Single-process pure Python; no new dependencies.

Command: `uv run python -m playground.visibility.run --counts 32 96 256 --repeats 3 --samples 1024`.

Times include everything through 2D Authoring, without export or oracle. Three fresh builds per case.

| Density | Faces | Fragments | BSP median (ms) | Min–max (ms) | Centroid median (ms) | BSP / baseline ray errors |
|---|---:|---:|---:|---:|---:|---:|
| sparse | 32 | 33 | 11.0 | 10.6–11.1 | 3.9 | 0 / 0 |
| sparse | 96 | 114 | 47.3 | 45.2–48.4 | 12.6 | 0 / 1 |
| sparse | 256 | 366 | 157.7 | 157.3–159.6 | 31.1 | 0 / 5 |
| medium | 32 | 52 | 16.0 | 16.0–16.3 | 3.6 | 0 / 12 |
| medium | 96 | 244 | 91.5 | 89.2–92.8 | 11.7 | 0 / 22 |
| medium | 256 | 1329 | 419.6 | 413.7–449.8 | 31.2 | 0 / 81 |
| dense | 32 | 105 | 29.0 | 28.9–29.1 | 3.6 | 0 / 119 |
| dense | 96 | 835 | 232.2 | 232.0–246.6 | 11.7 | 0 / 109 |
| dense | 256 | 7427 | 2049.1 | 1857.6–2248.7 | 31.1 | 0 / 364 |

Each case uses 1,024 rays (half uniform-screen, half source-interior-targeted).
Zero sampled errors do not establish all-pixel or exact-arithmetic correctness.

## Interpretation

- Sparse 256-face output is around 0.16 seconds; dense 256-face output is around 2 seconds.
- The dense case grows from 256 faces to 7,427 fragments. Splitting and Authoring allocation both matter.
- This is a deliberately unoptimized BSP prototype, not a bound on pdl performance or a guarantee for other scenes.
- Supporting planes also cut disjoint faces. Projected-overlap pruning and more careful partition selection are possible future work.
- Current centroid ordering is faster, but loses visibility correctness in these scenes.

Raw data and every scene SVG are generated under `output/`; rerunning regenerates them.
See the bilingual READMEs for generation, tolerances, unsupported inputs and exact timing boundaries.


## Production library run

The formal `Scene3D.project()` implementation was measured on 2026-10-28
with `uv run python -m playground.visibility.library` on the same platform.
Each call includes source capture, BSP, projection, source correspondence and
2D Authoring construction. Three fresh calls per case; generation, extraction
of returned polygons, ray checks and export are outside the clock. The oracle
reads the **actual public output**, not the prototype's fragments.

| Density | Faces | Fragments | Median (ms) | Min–max (ms) | Ray errors / 1024 |
|---|---:|---:|---:|---:|---:|
| sparse | 32 | 33 | 10.6 | 10.6–11.6 | 0 |
| sparse | 96 | 114 | 44.5 | 44.5–44.8 | 0 |
| sparse | 256 | 366 | 156.6 | 153.5–162.2 | 0 |
| medium | 32 | 52 | 15.5 | 15.4–15.6 | 0 |
| medium | 96 | 244 | 84.6 | 84.5–85.7 | 0 |
| medium | 256 | 1329 | 384.8 | 372.5–386.7 | 0 |
| dense | 32 | 105 | 26.1 | 25.7–26.3 | 0 |
| dense | 96 | 835 | 204.7 | 204.4–216.9 | 0 |
| dense | 256 | 7427 | 1709.0 | 1586.4–1736.8 | 0 |

Raw results: `output/library-results.json`, `output/library-timings.csv`;
scene images: `output/library-{density}-{count}.svg`. The earlier table is the
frozen prototype measurement; small speed differences are not a controlled
optimization comparison. The same floating/sampling caveats apply.
