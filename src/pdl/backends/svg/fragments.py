"""Native dvisvgm SVG embedding with namespaced resources."""

from xml.etree import ElementTree as ET

from pdl.author.transform.affine import AffineTransform as Transform
from pdl.author.transform.affine import Scaling, Translation
from pdl.author.util.tex import BP_TO_MM, TeXLayout


def fragment_svg(layout: TeXLayout, transform: Transform, prefix: str, fill: str) -> str:
    """Namespace fragment resources and place its baseline in pdl coordinates."""
    root = ET.fromstring(layout.svg)
    identifiers = {
        element.attrib["id"]: prefix + element.attrib["id"]
        for element in root.iter()
        if "id" in element.attrib
    }
    for element in root.iter():
        for key, value in tuple(element.attrib.items()):
            if key == "id":
                element.set(key, identifiers[value])
            elif value.startswith("#") and value[1:] in identifiers:
                element.set(key, "#" + identifiers[value[1:]])
            else:
                for old, new in identifiers.items():
                    value = value.replace(f"url(#{old})", f"url(#{new})")
                element.set(key, value)
    placement = (
        transform @ Scaling(BP_TO_MM, -BP_TO_MM) @ Translation(-layout.origin_x, -layout.origin_y)
    )
    matrix = " ".join(format(v, ".12g") for v in placement.values)
    return (
        f'<g fill="{fill}" transform="matrix({matrix})">'
        + "".join(ET.tostring(child, encoding="unicode") for child in root)
        + "</g>"
    )
