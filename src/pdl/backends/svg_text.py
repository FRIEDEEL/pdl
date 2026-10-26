"""SVG placement of independently typeset TeX fragments."""

from pdl.backends.svg_geometry import color
from pdl.geometry import point
from pdl.paint import BLACK, Style
from pdl.scene import Drawing
from pdl.tex import TeX
from pdl.tex_svg import fragment_svg
from pdl.transforms import Transform


def render_tex(tex: TeX, drawing: Drawing, prefix: str) -> str:
    paint = drawing.style or Style(stroke=None, fill=BLACK)
    if paint.stroke is not None:
        raise ValueError("TeX supports fill-only paint; use Style(stroke=None, fill=...).")
    if paint.fill is None:
        return ""
    p = point(tex.position)
    return fragment_svg(
        tex.layout, drawing.transform @ Transform.translate(p.x, p.y), prefix, color(paint.fill)
    )
