"""Generate and compile all examples while mirroring their source directories.

Run from the repository root: ``uv run python -m examples.tools.render_all``.
"""

import argparse
import inspect
from pathlib import Path

from examples._shared import export, output_base
from examples.composition.components import example as composition
from examples.composition.sandwich import example as sandwich
from examples.coordinates.relationships import example as coordinates
from examples.diagrams.nodes import example as nodes
from examples.diagrams.vacuum import example as vacuum
from examples.geometry.gallery import gallery
from examples.relationships.anchors import example as anchors
from examples.relationships.anchors import export_variants
from examples.relationships.instances import example as instances
from examples.spatial.curved_solids import example as curved_solids
from examples.spatial.curved_solids import views as curved_views
from examples.spatial.d10 import example as d10
from examples.spatial.material_probe import example as material_probe
from examples.spatial.material_probe import views as material_views
from examples.spatial.microscope import example as microscope
from examples.spatial.microscope import focus_detail
from examples.spatial.planes import example as planes
from examples.spatial.platonic_solids import example as platonic_solids
from examples.spatial.visibility import example as visibility
from examples.text.labels import example as text
from examples.text.tex import example as tex
from examples.text.tex import export_embedding
from pdl.rendering.tikz.compiler import TikZMode, compile_pdf


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tikz-mode", choices=("auto", "tex", "pdf"), default="auto")
    parser.add_argument("--keep-intermediates", action="store_true")
    args = parser.parse_args()
    mode: TikZMode = args.tikz_mode

    def compile_tikz(base: Path) -> None:
        compile_pdf(base.with_suffix(".tex"), mode=mode, keep_intermediates=args.keep_intermediates)

    for build in (
        gallery,
        composition,
        sandwich,
        text,
        tex,
        nodes,
        vacuum,
        anchors,
        instances,
        coordinates,
        planes,
        platonic_solids,
        curved_solids,
        d10,
        visibility,
        material_probe,
        microscope,
    ):
        canvas = build()
        source = inspect.getfile(build)
        base = export(canvas, source, tikz_mode="tex")
        if build is tex:
            export_embedding(canvas)
        compile_tikz(base)
        if build is material_probe:
            views_base = base.with_name("material_probe-views")
            study = material_views()
            study.save(views_base.with_suffix(".svg"))
            study.save(views_base.with_suffix(".tex"), backend="tikz", tikz_mode="tex")
            compile_tikz(views_base)
        if build is microscope:
            detail_base = base.with_name("microscope-focus")
            detail = focus_detail()
            detail.save(detail_base.with_suffix(".svg"))
            detail.save(detail_base.with_suffix(".tex"), backend="tikz", tikz_mode="tex")
            compile_tikz(detail_base)
        if build is anchors:
            for variant in export_variants(canvas):
                compile_tikz(variant)
        print(f"Generated outputs at {base}", flush=True)
    curves_base = output_base(inspect.getfile(curved_solids)).with_name("curved_solids-views")
    curved_canvas = curved_views()
    curved_canvas.save(curves_base.with_suffix(".svg"))
    curved_canvas.save(curves_base.with_suffix(".tex"), backend="tikz", tikz_mode="tex")
    compile_tikz(curves_base)
    embedded = output_base(inspect.getfile(tex)).parent / "tex-embedded.tex"
    compile_tikz(embedded)


if __name__ == "__main__":
    main()
