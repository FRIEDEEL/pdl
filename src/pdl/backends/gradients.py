"""Equivalent normalized-bounds gradient placement for SVG and PDF shadings."""

from dataclasses import replace
from decimal import Decimal

from pdl.author.entity.base import Entity
from pdl.author.geometry.base import Geometry
from pdl.author.geometry.point import as_point as point
from pdl.author.geometry.queries import bounds_of
from pdl.author.style import LinearGradient, RadialGradient, Style
from pdl.author.transform.affine import AffineTransform, Scaling, Translation
from pdl.backends.formatting import number
from pdl.backends.svg.geometry import color
from pdl.backends.tikz.geometry import paint_options, path_data


def gradient_matrix(
    geometry: Geometry,
    placement: AffineTransform,
    gradient: LinearGradient | RadialGradient | None = None,
) -> AffineTransform:
    if gradient is not None and gradient.frame is not None:
        origin, x, y = gradient.frame
        return placement @ AffineTransform(
            x[0] - origin[0],
            x[1] - origin[1],
            y[0] - origin[0],
            y[1] - origin[1],
            origin[0],
            origin[1],
        )
    box = bounds_of(geometry)
    return placement @ Translation(box.left, box.bottom) @ Scaling(box.width, box.height)


def svg_gradient(
    gradient: LinearGradient | RadialGradient, matrix: AffineTransform, name: str
) -> str:

    transform = " ".join(number(v) for v in matrix.values)
    common = (
        f'id="{name}" gradientUnits="userSpaceOnUse" '
        f'gradientTransform="matrix({transform})" spreadMethod="pad" '
        'color-interpolation="sRGB"'
    )
    if isinstance(gradient, LinearGradient):
        start, end = point(gradient.start), point(gradient.end)
        tag = "linearGradient"
        attrs = (
            f'x1="{number(start.x)}" y1="{number(start.y)}" '
            f'x2="{number(end.x)}" y2="{number(end.y)}"'
        )
    else:
        center = point(gradient.center)
        tag = "radialGradient"
        attrs = f'cx="{number(center.x)}" cy="{number(center.y)}" r="{number(gradient.radius)}"'
    stops = "".join(
        f'<stop offset="{number(s.offset)}" stop-color="{color(s.color)}"/>' for s in gradient.stops
    )
    return f"<defs><{tag} {common} {attrs}>{stops}</{tag}></defs>"


def _function(gradient: LinearGradient | RadialGradient) -> str:
    def scalar(value: float) -> str:
        # PDF calculator functions require decimal literals, not exponent notation.
        return format(Decimal(number(value)), "f")

    # Input is x,y in a 100bp square. Convert to normalized distance t.
    if isinstance(gradient, LinearGradient):
        start, end = point(gradient.start), point(gradient.end)
        dx, dy = end.x - start.x, end.y - start.y
        length = dx * dx + dy * dy
        distance = (
            f"100 div {scalar(start.y)} sub {scalar(dy)} mul exch "
            f"100 div {scalar(start.x)} sub {scalar(dx)} mul add {scalar(length)} div"
        )
    else:
        center = point(gradient.center)
        distance = (
            f"100 div {scalar(center.y)} sub dup mul exch "
            f"100 div {scalar(center.x)} sub dup mul add sqrt {scalar(gradient.radius)} div"
        )
    # Clamp to the padded range using only PDF type-4 calculator operators.
    distance += " dup 0 lt { pop 0 } if dup 1 gt { pop 1 } if "
    result = "pop " + " ".join(
        scalar(v)
        for v in (
            gradient.stops[-1].color.red,
            gradient.stops[-1].color.green,
            gradient.stops[-1].color.blue,
        )
    )
    for left, right in reversed(tuple(zip(gradient.stops, gradient.stops[1:]))):
        pairs = (
            (left.color.red, right.color.red),
            (left.color.green, right.color.green),
            (left.color.blue, right.color.blue),
        )
        interpolation = f"{scalar(left.offset)} sub {scalar(right.offset - left.offset)} div "
        for index, (a, b) in enumerate(pairs):
            interpolation += (
                "" if index == 2 else "dup "
            ) + f"{scalar(b - a)} mul {scalar(a)} add "
            if index != 2:
                interpolation += "exch "
        result = f"dup {scalar(right.offset)} le {{ {interpolation} }} {{ {result} }} ifelse"
    return distance + result


def tikz_gradient(geometry: Geometry, drawing: Entity, style: Style, name: str) -> str:

    gradient = style.fill
    assert isinstance(gradient, (LinearGradient, RadialGradient))
    matrix = gradient_matrix(geometry, AffineTransform(), gradient)
    placed = geometry
    if matrix.determinant == 0:
        return (
            "\\path["
            + ",".join(paint_options(replace(style, fill=None)))
            + "] "
            + path_data(placed)
            + ";"
        )
    # Shading is 100bp square; PGF text uses physical big points.
    matrix = matrix @ Scaling(1 / (100 * 25.4 / 72))
    a, b, c, d, e, f = (number(v) for v in matrix.values)
    rule = "even odd rule" if style.fill_rule == "evenodd" else "nonzero rule"
    fill = (
        f"\\pgfdeclarefunctionalshading{{{name}}}{{\\pgfpointorigin}}{{\\pgfpoint{{100bp}}{{100bp}}}}{{}}{{{_function(gradient)}}}\n"
        f"\\begin{{scope}}[{rule}]\n"
        f"\\clip {path_data(placed)};\n"
        f"\\pgfsetfillopacity{{{number(style.opacity)}}}\n"
        f"\\pgftransformcm{{{a}}}{{{b}}}{{{c}}}{{{d}}}{{\\pgfpoint{{{e}mm}}{{{f}mm}}}}\n"
        "\\pgflowlevelsynccm\n"
        f"\\pgftext[left,bottom]{{\\pgfuseshading{{{name}}}}}\n"
        "\\end{scope}\n"
    )
    return (
        fill
        + "\\path["
        + ",".join(paint_options(replace(style, fill=None)))
        + "] "
        + path_data(placed)
        + ";"
    )
