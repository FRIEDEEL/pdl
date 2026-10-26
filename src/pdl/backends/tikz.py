"""TikZ document orchestration and object dispatch."""

from pdl.backends._format import number
from pdl.backends.tikz_geometry import color, path_data
from pdl.backends.tikz_text import configuration, preamble, render_tex
from pdl.canvas import Canvas
from pdl.paint import BLACK, Style
from pdl.scene import Composite, Drawing, walk
from pdl.tex import TeX
from pdl.text import Text
from pdl.transforms import Transform, placed_geometry


def render_drawing(drawing: Drawing) -> str:
    geometry = drawing.geometry
    if isinstance(geometry, TeX):
        return render_tex(geometry, drawing)
    if isinstance(geometry, Composite):
        raise TypeError("Expected a geometry leaf.")
    paint = drawing.style or (
        Style(stroke=None, fill=BLACK) if isinstance(geometry, Text) else Style()
    )
    if drawing.transform != Transform():
        geometry = placed_geometry(geometry, drawing.transform)
    s = paint
    stroke = s.stroke if s.line_width > 0 else None
    options = [
        f"draw={color(stroke) if stroke is not None else 'none'}",
        f"fill={color(s.fill) if s.fill is not None else 'none'}",
        f"line width={number(s.line_width)}mm",
        f"line cap={s.line_cap}",
        f"line join={s.line_join}",
        "miter limit=10",
        "even odd rule" if s.fill_rule == "evenodd" else "nonzero rule",
    ]
    return "\\path[" + ",".join(options) + "] " + path_data(geometry) + ";"


def picture(canvas: Canvas) -> str:
    """Return a TikZ picture fragment for embedding in another document."""
    configuration(canvas)
    w, h = number(canvas.width), number(canvas.height)
    lines = [
        r"\begin{tikzpicture}[x=1mm,y=1mm]",
        f"\\path[use as bounding box] (0,0) rectangle ({w},{h});",
        f"\\clip (0,0) rectangle ({w},{h});",
    ]
    lines.extend(render_drawing(drawing) for drawing in walk(canvas.drawings))
    lines.append(r"\end{tikzpicture}")
    return "\n".join(lines) + "\n"


def render(canvas: Canvas, *, standalone: bool = True) -> str:
    if not standalone:
        return picture(canvas)
    config = configuration(canvas)
    engine = f"% !TeX program = {config.engine}\n" if config else ""
    return (
        engine
        + r"\documentclass[tikz,border=0pt]{standalone}"
        + "\n"
        + preamble(canvas)
        + r"\begin{document}"
        + "\n"
        + picture(canvas)
        + r"\end{document}"
        + "\n"
    )
