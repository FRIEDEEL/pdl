"""Native image placement shared by SVG and TikZ document adapters."""

from base64 import b64encode

from pdl.author.entity.base import Entity as Drawing
from pdl.author.geometry.image import Image
from pdl.author.geometry.point import as_point as point
from pdl.backends.formatting import number
from pdl.backends.tikz.geometry import path_data


def svg_image(image: Image, drawing: Drawing, prefix: str) -> str:
    p = point((0, 0))
    x, y, width, height = image.content_box()
    matrix = " ".join(number(v) for v in image.mapping.values)
    encoded = b64encode(image.data).decode("ascii")
    clip = prefix + "image-clip"
    opacity = drawing.effective_style.opacity
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

    x, y, width, height = image.content_box()
    a, b, c, d, e, f = (number(v) for v in image.mapping.values)
    clip = image.to_path()
    opacity = drawing.effective_style.opacity
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
