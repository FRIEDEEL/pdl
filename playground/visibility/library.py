"""Benchmark the public production Scene3D.project path against the ray oracle.

Run: uv run python -m playground.visibility.library
The frozen experimental prototype and its old measurements remain available.
"""

import csv
import json
import platform
from pathlib import Path
from statistics import median
from time import perf_counter

from pdl import Canvas, Point, ProjectedScene, Scene3D
from pdl.author.entity.capture import walk
from pdl.author.geometry.shapes import Polygon
from playground.visibility.oracle import check
from playground.visibility.run import baseline
from playground.visibility.scenes import CAMERA, random_faces

OUTPUT = Path(__file__).parent / "output"


def projected_polygons(snapshot: ProjectedScene) -> tuple[tuple[int, tuple[Point, ...]], ...]:
    """Read the actual public 2D paint list; no BSP internals participate in checking."""
    polygons: list[tuple[int, tuple[Point, ...]]] = []
    for child, source in zip(snapshot.children, snapshot.source_faces):
        geometry = next(walk((child,))).geometry
        if not isinstance(geometry, Polygon) or source is None:
            raise TypeError("Expected a polygon fragment with source correspondence.")
        points = tuple(p if isinstance(p, Point) else Point(*p) for p in geometry.points)
        polygons.append((source[0], points))
    return tuple(polygons)


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, object]] = []
    for density_name, density in (("sparse", 0.05), ("medium", 0.16), ("dense", 0.32)):
        for count in (32, 96, 256):
            faces = random_faces(count, density, 20261028 + count)
            objects = baseline(faces).objects
            scene = Scene3D(objects, CAMERA, light=None, visibility="bsp")
            times: list[float] = []
            start = perf_counter()
            snapshot = scene.project()
            times.append(perf_counter() - start)
            for _ in range(2):
                start = perf_counter()
                snapshot = scene.project()
                times.append(perf_counter() - start)
            result = check(
                faces,
                (),
                CAMERA,
                samples=1024,
                seed=91 + count,
                painted_polygons=projected_polygons(snapshot),
            )
            row: dict[str, object] = {
                "density": density_name,
                "faces": count,
                "fragments": len(snapshot.children),
                "seconds_median": median(times),
                "seconds_min": min(times),
                "seconds_max": max(times),
                "samples": result.samples,
                "covered": result.covered,
                "mismatches": result.mismatches,
            }
            print(json.dumps(row), flush=True)
            rows.append(row)
            if result.mismatches:
                raise RuntimeError("Production visibility differs from the ray oracle.")
            canvas = Canvas(200, 200)
            canvas.add(snapshot.copy().translate(100, 100))
            canvas.save(OUTPUT / f"library-{density_name}-{count}.svg")
    (OUTPUT / "library-results.json").write_text(
        json.dumps(
            {
                "python": platform.python_version(),
                "platform": platform.platform(),
                "repeats": 3,
                "cases": rows,
            },
            indent=2,
        )
        + "\n"
    )
    with (OUTPUT / "library-timings.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()
