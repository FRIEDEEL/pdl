"""Native image placement shared by SVG and TikZ document adapters."""

from base64 import b64encode

from pdl.author.composition import Drawing
from pdl.author.image import Image
from pdl.backends.formatting import number
from pdl.foundation.geometry.primitives import point


def svg_image(image: Image, drawing: Drawing, prefix: str) -> str:
    p = point(image.position)
    x, y, width, height = image.content_box()
    matrix = " ".join(number(v) for v in drawing.transform.values)
    encoded = b64encode(image.data).decode("ascii")
    clip = prefix + "image-clip"
    opacity = 1 if drawing.style is None else drawing.style.opacity
    return (
        f'<g opacity="{number(opacity)}" transform="matrix({matrix})"><defs><clipPath id="{clip}">'
        f'<rect x="{number(p.x)}" y="{number(p.y)}" width="{number(image.width)}" '
        f'height="{number(image.height)}"/></clipPath></defs>'
        f'<g clip-path="url(#{clip})"><image x="{number(x)}" y="{number(-y - height)}" '
        f'width="{number(width)}" height="{number(height)}" preserveAspectRatio="none" '
        f'transform="scale(1 -1)" href="data:image/{image.format};base64,{encoded}"/>'
        "</g></g>"
    )


def tikz_image(image: Image, drawing: Drawing) -> str:
    from pdl.author.shapes import Rectangle
    from pdl.backends.geometry import placed_geometry
    from pdl.backends.tikz.geometry import path_data

    x, y, width, height = image.content_box()
    a, b, c, d, e, f = (number(v) for v in drawing.transform.values)
    clip = placed_geometry(Rectangle(image.position, image.width, image.height), drawing.transform)
    opacity = 1 if drawing.style is None else drawing.style.opacity
    return (
        f"\\begin{{scope}}[opacity={number(opacity)}]\n"
        f"\\clip {path_data(clip)};\n"
        f"\\pgftransformcm{{{a}}}{{{b}}}{{{c}}}{{{d}}}{{\\pgfpoint{{{e}mm}}{{{f}mm}}}}\n"
        "\\pgflowlevelsynccm\n"
        f"\\pgftext[left,bottom,at={{\\pgfpoint{{{number(x)}mm}}{{{number(y)}mm}}}}]"
        f"{{\\includegraphics[width={number(width)}mm,height={number(height)}mm]"
        + "{\\detokenize{"
        + image.asset().as_posix()
        + "}}}\n"
        "\\end{scope}"
    )
