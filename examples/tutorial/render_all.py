"""Generate the tutorial SVG images without requiring a TeX installation.

Run from the repository root: uv run python -m examples.tutorial.render_all
"""

import runpy


def main() -> None:
    for name in (
        "hello_world",
        "shapes",
        "coordinates",
        "stroke",
        "fill",
        "fill_only",
        "colored_shapes",
    ):
        runpy.run_module(f"examples.tutorial.basics.{name}", run_name="__main__")
        print(f"Generated examples/output/tutorial/basics/{name}.svg", flush=True)


if __name__ == "__main__":
    main()
