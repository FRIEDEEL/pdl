"""SVG document orchestration and object dispatch."""

from pdl.backends._format import number
from pdl.backends.svg_geometry import shape, style_attributes
from pdl.canvas import Canvas
from pdl.paint import Style
from pdl.scene import Composite, Drawing, walk
from pdl.transforms import Transform, transform_path


def render_drawing(drawing: Drawing) -> str:
    geometry = drawing.geometry
    if isinstance(geometry, Composite):
        raise TypeError("Expected a geometry leaf.")
    if drawing.transform != Transform():
        geometry = transform_path(geometry, drawing.transform)
    return f"  <{shape(geometry)} {style_attributes(drawing.style or Style())}/>"


def render(canvas: Canvas) -> str:
    w, h = number(canvas.width), number(canvas.height)
    elements = [render_drawing(drawing) for drawing in walk(canvas.drawings)]
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}mm" height="{h}mm" '
        f'viewBox="0 0 {w} {h}" overflow="hidden">\n'
        f'<g transform="translate(0 {h}) scale(1 -1)">\n' + "\n".join(elements) + "\n</g>\n</svg>\n"
    )
