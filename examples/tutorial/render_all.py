"""Generate all tutorial SVGs and the TeX examples' native PDFs.

Requires XeLaTeX and dvisvgm for chapters using TeX.
Run: uv run python -m examples.tutorial.render_all
"""

import runpy

MODULES = (
    "advanced.viewport_clip",
    "advanced.viewport_fit",
    "advanced.viewport_auto_size",
    "basics.hello_world",
    "basics.shapes",
    "basics.coordinates",
    "basics.stroke",
    "basics.fill",
    "basics.fill_only",
    "basics.colored_shapes",
    "layout.circle_first",
    "layout.rectangle_first",
    "text.labels",
    "text.formula",
    "geometry.translation",
    "geometry.rotation",
    "geometry.scaling",
    "geometry.local_coordinates",
    "layout.anchors",
    "layout.captured_anchors",
    "layout.groups",
    "geometry.outline",
    "geometry.curve",
    "geometry.queries",
    "advanced.resolved",
    "advanced.fill_rules",
    "advanced.tex_pipeline",
)


def main() -> None:
    for module in MODULES:
        runpy.run_module(f"examples.tutorial.{module}", run_name="__main__")
        print(f"Generated tutorial example: {module}", flush=True)


if __name__ == "__main__":
    main()
