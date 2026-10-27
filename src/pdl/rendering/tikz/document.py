"""TikZ document orchestration and object dispatch."""

from pdl.components.nodes import Node
from pdl.geometry.transforms import Transform, placed_geometry
from pdl.media.images import Image
from pdl.rendering.formatting import number
from pdl.rendering.images import tikz_image
from pdl.rendering.tikz.geometry import paint_options, path_data
from pdl.rendering.tikz.nodes import render_node, supports
from pdl.rendering.tikz.text import configuration, font_commands, preamble, render_tex, render_text
from pdl.rendering.traversal import prepare
from pdl.scene.canvas import Canvas
from pdl.scene.composition import Composite, Drawing
from pdl.scene.paint import BLACK, LinearGradient, RadialGradient, Style
from pdl.typography.plain import Font, Text
from pdl.typography.tex import TeX


def render_drawing(drawing: Drawing, commands: dict[Font, str], prefix: str = "pdlgradient") -> str:
    geometry = drawing.geometry
    if isinstance(geometry, Image):
        return tikz_image(geometry, drawing)
    if isinstance(geometry, Node):
        return render_node(geometry, drawing, commands)
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
        from pdl.rendering.gradients import tikz_gradient

        return tikz_gradient(geometry, drawing, paint, prefix)
    if drawing.transform != Transform():
        geometry = placed_geometry(geometry, drawing.transform)
    return "\\path[" + ",".join(paint_options(paint)) + "] " + path_data(geometry) + ";"


def picture(canvas: Canvas, drawings: tuple[Drawing, ...]) -> str:
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


def render(canvas: Canvas, *, standalone: bool = True) -> str:
    drawings = tuple(prepare(canvas.drawings, supports))
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
