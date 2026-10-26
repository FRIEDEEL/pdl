"""Generate and compile all examples while mirroring their source directories.

Run from the repository root: ``uv run python -m examples.tools.render_all``.
"""

import inspect
import subprocess
from pathlib import Path

from examples._shared import export, output_base
from examples.composition.components import example as composition
from examples.diagrams.nodes import example as nodes
from examples.diagrams.vacuum import example as vacuum
from examples.geometry.gallery import gallery
from examples.relationships.anchors import example as anchors
from examples.relationships.anchors import export_variants
from examples.relationships.instances import example as instances
from examples.text.labels import example as text
from examples.text.tex import example as tex
from examples.text.tex import export_embedding


def compile_tikz(base: Path) -> None:
    result = subprocess.run(
        [
            "xelatex",
            "-no-shell-escape",
            "-interaction=nonstopmode",
            "-halt-on-error",
            base.with_suffix(".tex").name,
        ],
        cwd=base.parent,
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    if result.returncode:
        raise RuntimeError(result.stdout[-8000:])


def main() -> None:
    for build in (gallery, composition, text, tex, nodes, vacuum, anchors, instances):
        canvas = build()
        source = inspect.getfile(build)
        base = export(canvas, source)
        if build is tex:
            export_embedding(canvas)
        compile_tikz(base)
        if build is anchors:
            for variant in export_variants(canvas):
                compile_tikz(variant)
        print(f"Generated {base.with_suffix('.svg')}, .tex and .pdf", flush=True)
    embedded = output_base(inspect.getfile(tex)).parent / "tex-embedded.tex"
    compile_tikz(embedded)


if __name__ == "__main__":
    main()
