"""Benchmark through 2D Authoring and export seeded perspective comparisons.

Run: uv run python -m playground.visibility.run
Use --counts 32 96 256 --repeats 3 to change workload. Outputs stay local.
"""

import argparse
import csv
import json
import platform
from dataclasses import asdict
from pathlib import Path
from statistics import median
from time import perf_counter

from examples._shared import latin_font
from pdl import (
    Canvas,
    Color,
    PerspectiveCamera,
    Polyhedron,
    Scaling,
    Scene3D,
    Style,
    Text,
    Translation,
)
from playground.visibility.bsp import Face, project
from playground.visibility.oracle import check
from playground.visibility.scenes import CAMERA, crossing, cycle, max_trap, random_faces

OUTPUT = Path(__file__).parent / "output"


def baseline(faces: tuple[Face, ...], camera: PerspectiveCamera = CAMERA) -> Scene3D:
    return Scene3D(
        tuple(
            Polyhedron(
                face.vertices,
                (tuple(range(len(face.vertices))),),
                color=face.color,
                line_width=0.18,
            )
            for face in faces
        ),
        camera,
        light=None,
        visibility="centroid",
    )


def centroid_order(faces: tuple[Face, ...]) -> tuple[Face, ...]:
    return tuple(
        sorted(faces, key=lambda f: sum(CAMERA.depth(p) for p in f.vertices) / len(f.vertices))
    )


def poster() -> None:
    """Keep old/new views side-by-side using identical opaque source colors."""
    canvas = Canvas(360, 540)
    font = latin_font()
    ink = Style(stroke=None, fill=Color(0.1, 0.17, 0.24))

    def label(value: str, x: float, y: float, size: float = 11) -> None:
        canvas.draw(Text(value, font=font, position=(x, y), size=size), ink)

    label("Perspective visibility / centroid vs BSP", 12, 523, 23)
    label("Centroid ordering (reference)", 20, 508)
    label("BSP splitting + painter order", 192, 508)
    cases = (
        ("A / Parallel faces: global depth extrema can mislead", max_trap()),
        ("B / Intersecting planes: front/back changes across the crossing", crossing()),
        ("C / Disjoint ribbons: no whole-face ordering can resolve this cycle", cycle()),
        ("D / Seeded random convex faces: dense intersections", random_faces(36, 0.32, 20261028)),
    )
    for row, (title, faces) in enumerate(cases):
        y = 390 - row * 120
        label(title, 12, y + 102, 10)
        before = baseline(faces).project()
        after, metrics, fragments = project(faces, CAMERA)
        old_check = check(faces, centroid_order(faces), CAMERA, samples=1200)
        new_check = check(faces, fragments, CAMERA, samples=1200)
        points = tuple(CAMERA.project(p) for face in faces for p in face.vertices)
        left, right = min(p.x for p in points), max(p.x for p in points)
        bottom, top = min(p.y for p in points), max(p.y for p in points)
        scale = min(0.8, 140 / (right - left), 80 / (top - bottom))
        for x, scene in ((87, before), (267, after)):
            transform = Translation(
                x - scale * (left + right) / 2, y + 52 - scale * (bottom + top) / 2
            ) @ Scaling(scale)
            canvas.add(scene.copy().apply_transform(transform))
        label(f"Ray-check mismatches: {old_check.mismatches}/{old_check.samples}", 20, y + 3, 9)
        label(
            f"{metrics.fragments} fragments / {metrics.total_seconds * 1000:.1f} ms to Authoring",
            192,
            y + 3,
            9,
        )
        label(f"Ray-check mismatches: {new_check.mismatches}/{new_check.samples}", 192, y - 3, 8)
    canvas.save(OUTPUT / "comparison.svg")
    canvas.save(OUTPUT / "comparison.tex", backend="tikz", tikz_mode="pdf")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--counts", type=int, nargs="+", default=[32, 96, 256])
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--samples", type=int, default=256)
    args = parser.parse_args()
    if min(args.counts) <= 0 or args.repeats <= 0 or args.samples <= 0:
        parser.error("counts, repeats and samples must be positive")
    OUTPUT.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, object]] = []
    for density_name, density in (("sparse", 0.05), ("medium", 0.16), ("dense", 0.32)):
        for count in args.counts:
            # Every case uses an independent, deterministic seed. Generation is untimed.
            seed = 20261028 + count
            faces = random_faces(count, density, seed)
            baseline_scene = baseline(faces)
            old_times: list[float] = []
            for _ in range(args.repeats):
                start = perf_counter()
                baseline_scene.project()
                old_times.append(perf_counter() - start)
            author, metrics, fragments = project(faces, CAMERA)
            times: list[float] = [metrics.total_seconds]
            for _ in range(args.repeats - 1):
                author, metrics, fragments = project(faces, CAMERA)
                times.append(metrics.total_seconds)
            result = check(faces, fragments, CAMERA, samples=args.samples, seed=91 + count)
            old_result = check(
                faces, centroid_order(faces), CAMERA, samples=args.samples, seed=91 + count
            )
            row: dict[str, object] = {
                "density": density_name,
                "radius_fraction": density,
                "faces": count,
                "seed": seed,
                "fragments": metrics.fragments,
                "splits": metrics.splits,
                "classifications": metrics.classifications,
                "tree_depth": metrics.max_depth,
                "seconds_median": median(times),
                "seconds_min": min(times),
                "seconds_max": max(times),
                "centroid_seconds_median": median(old_times),
                "samples": result.samples,
                "covered_samples": result.covered,
                "mismatches": result.mismatches,
                "centroid_mismatches": old_result.mismatches,
                "build_seconds_last": metrics.build_seconds,
                "author_seconds_last": metrics.author_seconds,
            }
            rows.append(row)
            print(json.dumps(row), flush=True)
            # Export and Canvas evaluation are deliberately outside all measured intervals.
            canvas = Canvas(200, 200)
            canvas.add(author.copy().translate(100, 100))
            canvas.save(OUTPUT / f"{density_name}-{count}.svg")
            if result.mismatches:
                raise RuntimeError("Visibility oracle found a mismatch; inspect the case.")
    with (OUTPUT / "timings.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    (OUTPUT / "results.json").write_text(
        json.dumps(
            {
                "python": platform.python_version(),
                "platform": platform.platform(),
                "repeats": args.repeats,
                "camera": asdict(CAMERA),
                "cases": rows,
            },
            indent=2,
        )
        + "\n"
    )
    poster()
    print(f"Outputs: {OUTPUT}", flush=True)


if __name__ == "__main__":
    main()
