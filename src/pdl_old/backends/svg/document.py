"""SVG document orchestration and object dispatch."""

from pdl.author.composition import Composite, Drawing
from pdl.author.image import Image
from pdl.author.style import BLACK, LinearGradient, RadialGradient, Style
from pdl.author.tex import TeX
from pdl.author.text import Text
from pdl.backends.formatting import number
from pdl.backends.geometry import placed_geometry
from pdl.backends.images import svg_image
from pdl.backends.svg.geometry import shape, style_attributes
from pdl.backends.svg.text import render_tex, render_text
from pdl.backends.traversal import prepare
from pdl.canvas.records import Page
from pdl.foundation.geometry.transforms import Transform


def render_drawing(drawing: Drawing, prefix: str = "tex-") -> str:
    geometry = drawing.geometry
    if isinstance(geometry, Image):
        return svg_image(geometry, drawing, prefix)
    if isinstance(geometry, Text):
        return render_text(geometry, drawing)
    if isinstance(geometry, TeX):
        return render_tex(geometry, drawing, prefix)
    if isinstance(geometry, Composite):
        raise TypeError("Expected a geometry leaf.")
    paint = drawing.style or (
        Style(stroke=None, fill=BLACK) if isinstance(geometry, Text) else Style()
    )
    definition = ""
    gradient_id = None
    if isinstance(paint.fill, (LinearGradient, RadialGradient)):
        from pdl.backends.gradients import gradient_matrix, svg_gradient

        gradient_id = prefix + "gradient"
        definition = svg_gradient(
            paint.fill, gradient_matrix(geometry, drawing.transform), gradient_id
        )
    if drawing.transform != Transform():
        geometry = placed_geometry(geometry, drawing.transform)
    return definition + f"  <{shape(geometry)} {style_attributes(paint, gradient_id)}/>"


def render(canvas: Page) -> str:
    w, h = number(canvas.width), number(canvas.height)
    elements = [
        render_drawing(drawing, f"tex{i}-")
        for i, drawing in enumerate(prepare(canvas.drawings, lambda _: False))
    ]
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}mm" height="{h}mm" '
        f'viewBox="0 0 {w} {h}" overflow="hidden">\n'
        f'<g transform="translate(0 {h}) scale(1 -1)">\n' + "\n".join(elements) + "\n</g>\n</svg>\n"
    )
