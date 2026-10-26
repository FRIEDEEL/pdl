"""Embed converter-produced SVG fragments and lower monochrome outlines."""

from collections.abc import Callable
from typing import cast
from xml.etree import ElementTree as ET

from fontTools.svgLib.path.parser import parse_path  # pyright: ignore[reportMissingTypeStubs, reportUnknownVariableType]

from pdl.fonts import OutlinePen
from pdl.geometry import Path, Rectangle
from pdl.tex import BP_TO_MM, TeXLayout
from pdl.transforms import Transform, transform_path


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
        transform
        @ Transform.scale(BP_TO_MM, -BP_TO_MM)
        @ Transform.translate(-layout.origin_x, -layout.origin_y)
    )
    matrix = " ".join(format(v, ".12g") for v in placement.values)
    return (
        f'<g fill="{fill}" transform="matrix({matrix})">'
        + "".join(ET.tostring(child, encoding="unicode") for child in root)
        + "</g>"
    )


def outline_path(layout: TeXLayout) -> Path:
    """Lower the monochrome path/rectangle subset produced by dvisvgm.

    Rich SVG remains available through fragment embedding. Refuse unsupported
    elements rather than silently losing artwork during geometric lowering.
    """
    root = ET.fromstring(layout.svg)
    path = Path()
    parser = cast(Callable[[str, object], None], parse_path)
    for element in root.iter():
        tag = element.tag.rsplit("}", 1)[-1]
        if "transform" in element.attrib:
            raise ValueError("Transformed SVG fragments require native embedding.")
        if element.attrib.get("fill", "black") not in ("black", "#000", "#000000"):
            raise ValueError("Colored TeX fragments require native embedding.")
        if tag == "path":
            pen = OutlinePen()
            parser(element.attrib["d"], pen)
            path.extend(pen.path)
        elif tag == "rect":
            rectangle = Rectangle(
                (float(element.attrib.get("x", "0")), float(element.attrib.get("y", "0"))),
                float(element.attrib["width"]),
                float(element.attrib["height"]),
            )
            path.extend(rectangle)
        elif tag not in ("svg", "g", "defs", "title", "desc"):
            raise ValueError(f"SVG element {tag!r} requires native embedding.")
    return transform_path(
        path,
        Transform.scale(BP_TO_MM, -BP_TO_MM)
        @ Transform.translate(-layout.origin_x, -layout.origin_y),
    )
