"""SVG document orchestration and object dispatch."""

from pdl.author.entity.base import Entity
from pdl.author.geometry.image import Image
from pdl.author.geometry.tex import TeX
from pdl.author.geometry.text import Text
from pdl.author.style import LinearGradient, RadialGradient
from pdl.author.transform.affine import AffineTransform
from pdl.backends.formatting import number
from pdl.backends.gradients import gradient_matrix, svg_gradient
from pdl.backends.images import svg_image
from pdl.backends.svg.geometry import shape, style_attributes
from pdl.backends.svg.text import render_tex, render_text
from pdl.backends.traversal import walk
from pdl.canvas.records import Page


def render_drawing(drawing: Entity, prefix: str = "tex-") -> str:
    geometry = drawing.geometry
    if isinstance(geometry, Image):
        return svg_image(geometry, drawing, prefix)
    if isinstance(geometry, Text):
        return render_text(geometry, drawing)
    if isinstance(geometry, TeX):
        return render_tex(geometry, drawing, prefix)
    paint = drawing.effective_style
    definition = ""
    gradient_id = None
    if isinstance(paint.fill, (LinearGradient, RadialGradient)):
        gradient_id = prefix + "gradient"
        definition = svg_gradient(
            paint.fill, gradient_matrix(geometry, AffineTransform(), paint.fill), gradient_id
        )
    return definition + f"  <{shape(geometry)} {style_attributes(paint, gradient_id)}/>"


def render(canvas: Page) -> str:
    w, h = number(canvas.width), number(canvas.height)
    elements = [
        render_drawing(drawing, f"tex{i}-") for i, drawing in enumerate(walk(canvas.drawings))
    ]
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}mm" height="{h}mm" '
        f'viewBox="0 0 {w} {h}" overflow="hidden">\n'
        f'<g transform="translate(0 {h}) scale(1 -1)">\n' + "\n".join(elements) + "\n</g>\n</svg>\n"
    )
