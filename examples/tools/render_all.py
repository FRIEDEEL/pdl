"""Generate and compile all examples while mirroring their source directories.

Run from the repository root: ``uv run python -m examples.tools.render_all``.
"""

import inspect
import subprocess

from examples._shared import export, output_base
from examples.composition.components import example as composition
from examples.diagrams.nodes import example as nodes
from examples.diagrams.vacuum import example as vacuum
from examples.geometry.gallery import gallery
from examples.text.labels import example as text
from examples.text.tex import example as tex
from examples.text.tex import export_embedding


def main() -> None:
    for build in (gallery, composition, text, tex, nodes, vacuum):
        canvas = build()
        source = inspect.getfile(build)
        base = export(canvas, source)
        if build is tex:
            export_embedding(canvas)
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
        print(f"Generated {base.with_suffix('.svg')}, .tex and .pdf", flush=True)
    embedded = output_base(inspect.getfile(tex)).parent / "tex-embedded.tex"
    result = subprocess.run(
        [
            "xelatex",
            "-no-shell-escape",
            "-interaction=nonstopmode",
            "-halt-on-error",
            embedded.name,
        ],
        cwd=embedded.parent,
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    if result.returncode:
        raise RuntimeError(result.stdout[-8000:])


if __name__ == "__main__":
    main()
