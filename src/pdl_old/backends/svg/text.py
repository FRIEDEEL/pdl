"""SVG placement of independently typeset TeX fragments."""

from pdl.author.composition import Drawing
from pdl.author.style import BLACK, Color, Style
from pdl.author.tex import TeX
from pdl.author.text import Text
from pdl.backends.formatting import number
from pdl.backends.svg.geometry import color
from pdl.foundation.geometry.primitives import point
from pdl.foundation.geometry.transforms import Transform
from pdl.foundation.typography.fonts import font_family
from pdl.foundation.typography.shaping import PT_TO_MM
from pdl.foundation.typography.tex_svg import fragment_svg


def render_tex(tex: TeX, drawing: Drawing, prefix: str) -> str:
    t = drawing.transform
    if t.a * t.d - t.b * t.c == 0:
        return ""
    paint = drawing.style or Style(stroke=None, fill=BLACK)
    if paint.stroke is not None:
        raise ValueError("TeX supports fill-only paint; use Style(stroke=None, fill=...).")
    if paint.fill is None:
        return ""
    if not isinstance(paint.fill, Color):
        raise ValueError("Native Text and TeX require solid color fills.")
    p = point(tex.position)
    result = fragment_svg(
        tex.layout, drawing.transform @ Transform.translate(p.x, p.y), prefix, color(paint.fill)
    )
    return f'<g opacity="{number(paint.opacity)}">{result}</g>'


def render_text(text: Text, drawing: Drawing) -> str:
    """Keep ordinary labels as editable SVG text, referencing native fonts."""
    from html import escape

    paint = drawing.style or Style(stroke=None, fill=BLACK)
    if paint.stroke is not None:
        raise ValueError("Native Text supports fill-only paint; use fill and stroke=None.")
    if paint.fill is None:
        return ""
    if not isinstance(paint.fill, Color):
        raise ValueError("Native Text and TeX require solid color fills.")
    p = point(text.position)
    transform = drawing.transform @ Transform.scale(1, -1)
    matrix = " ".join(number(v) for v in transform.values)
    spans: list[str] = []
    for run in text.layout.runs:
        family = escape(font_family(str(run.font.file), run.font.index), quote=True)
        spans.append(
            f'<text x="{number(p.x + run.x)}" y="{number(-p.y - run.y)}" '
            f'font-family="{family}, sans-serif" font-size="{number(text.size * PT_TO_MM)}" '
            f'xml:space="preserve">{escape(run.text)}</text>'
        )
    return (
        f'<g opacity="{number(paint.opacity)}" fill="{color(paint.fill)}" '
        f'transform="matrix({matrix})">' + "".join(spans) + "</g>"
    )
