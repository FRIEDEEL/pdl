"""Mirror example source paths under the generated output tree."""

from pathlib import Path

from examples._shared.config import EXAMPLES, OUTPUT
from pdl import Canvas
from pdl.rendering.tikz.compiler import TikZMode


def output_base(source: str | Path) -> Path:
    relative = Path(source).resolve().relative_to(EXAMPLES).with_suffix("")
    destination = OUTPUT / relative
    destination.parent.mkdir(parents=True, exist_ok=True)
    return destination


def export(canvas: Canvas, source: str | Path, *, tikz_mode: TikZMode = "auto") -> Path:
    base = output_base(source)
    canvas.save(base.with_suffix(".svg"), backend="svg")
    canvas.save(base.with_suffix(".tex"), backend="tikz", tikz_mode=tikz_mode)
    return base
