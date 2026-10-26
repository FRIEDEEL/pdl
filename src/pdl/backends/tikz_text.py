"""Native TeX node rendering and document environment collection."""

from pdl.backends._format import number
from pdl.backends.tikz_geometry import color, coordinate
from pdl.canvas import Canvas
from pdl.geometry import point
from pdl.paint import BLACK, Style
from pdl.scene import Drawing, walk
from pdl.tex import TeX, TeXConfig


def configuration(canvas: Canvas) -> TeXConfig | None:
    configs = {
        drawing.geometry.config
        for drawing in walk(canvas.drawings)
        if isinstance(drawing.geometry, TeX)
    }
    if len(configs) > 1:
        raise ValueError("One native TikZ document requires a shared TeXConfig.")
    return next(iter(configs), None)


def preamble(canvas: Canvas) -> str:
    config = configuration(canvas)
    return r"\usepackage{tikz}" + "\n" + (config.latex_preamble() + "\n" if config else "")


def render_tex(tex: TeX, drawing: Drawing) -> str:
    paint = drawing.style or Style(stroke=None, fill=BLACK)
    if paint.stroke is not None:
        raise ValueError("Native TeX supports fill-only paint; use Style(stroke=None, fill=...).")
    if paint.fill is None:
        return ""
    a, b, c, d, e, f = (number(v) for v in drawing.transform.values)
    return (
        f"\\begin{{scope}}[cm={{{a},{b},{c},{d},({e},{f})}},transform shape]\n"
        + f"\\node[anchor=base west,inner sep=0pt,outer sep=0pt,text={color(paint.fill)}] "
        + f"at {coordinate(point(tex.position))} {{{tex.latex_body()}}};\n"
        + r"\end{scope}"
    )
