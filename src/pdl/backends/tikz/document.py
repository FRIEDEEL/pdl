"""TikZ document orchestration and object dispatch."""

from pdl.author.composition import Composite, Drawing
from pdl.author.image import Image
from pdl.author.style import BLACK, LinearGradient, RadialGradient, Style
from pdl.author.tex import TeX
from pdl.author.text import Text
from pdl.backends.formatting import number
from pdl.backends.geometry import placed_geometry
from pdl.backends.images import tikz_image
from pdl.backends.tikz.geometry import paint_options, path_data
from pdl.backends.tikz.text import configuration, font_commands, preamble, render_tex, render_text
from pdl.backends.traversal import prepare
from pdl.canvas.records import Page
from pdl.foundation.geometry.transforms import Transform
from pdl.foundation.typography.shaping import Font


def render_drawing(drawing: Drawing, commands: dict[Font, str], prefix: str = "pdlgradient") -> str:
    geometry = drawing.geometry
    if isinstance(geometry, Image):
        return tikz_image(geometry, drawing)
    if isinstance(geometry, Text):
        return render_text(geometry, drawing, commands)
    if isinstance(geometry, TeX):
        return render_tex(geometry, drawing)
    if isinstance(geometry, Composite):
        raise TypeError("Expected a geometry leaf.")
    paint = drawing.style or (
        Style(stroke=None, fill=BLACK) if isinstance(geometry, Text) else Style()
    )
    if isinstance(paint.fill, (LinearGradient, RadialGradient)):
        from pdl.backends.gradients import tikz_gradient

        return tikz_gradient(geometry, drawing, paint, prefix)
    if drawing.transform != Transform():
        geometry = placed_geometry(geometry, drawing.transform)
    return "\\path[" + ",".join(paint_options(paint)) + "] " + path_data(geometry) + ";"


def picture(canvas: Page, drawings: tuple[Drawing, ...]) -> str:
    """Return a TikZ picture fragment for embedding in another document."""
    configuration(drawings)
    w, h = number(canvas.width), number(canvas.height)
    lines = [
        r"\begin{tikzpicture}[x=1mm,y=1mm]",
        f"\\path[use as bounding box] (0,0) rectangle ({w},{h});",
        f"\\clip (0,0) rectangle ({w},{h});",
    ]
    commands = font_commands(drawings)
    lines.extend(
        render_drawing(drawing, commands, f"pdlgradient{i}") for i, drawing in enumerate(drawings)
    )
    lines.append(r"\end{tikzpicture}")
    return "\n".join(lines) + "\n"


def render(canvas: Page, *, standalone: bool = True) -> str:
    drawings = tuple(prepare(canvas.drawings, lambda _: False))
    if not standalone:
        return picture(canvas, drawings)
    config = configuration(drawings)
    engine = f"% !TeX program = {config.engine}\n" if config else ""
    return (
        engine
        + r"\documentclass[tikz,border=0pt]{standalone}"
        + "\n"
        + preamble(drawings)
        + r"\begin{document}"
        + "\n"
        + picture(canvas, drawings)
        + r"\end{document}"
        + "\n"
    )
