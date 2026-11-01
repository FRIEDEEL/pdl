"""Explicit monochrome TeX outline conversion for domain transformations."""

from collections.abc import Callable
from typing import cast
from xml.etree import ElementTree as ET

from fontTools.svgLib.path.parser import parse_path  # pyright: ignore[reportMissingTypeStubs, reportUnknownVariableType]

from pdl.author.geometry.path import Path
from pdl.author.geometry.typography import path_from_outline
from pdl.author.transform.affine import Scaling, Translation
from pdl.author.util.fonts import OutlinePen
from pdl.author.util.tex import BP_TO_MM, TeXLayout


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
            path.extend(path_from_outline(tuple(pen.commands)))
        elif tag == "rect":
            x, y = float(element.attrib.get("x", "0")), float(element.attrib.get("y", "0"))
            w, h = float(element.attrib["width"]), float(element.attrib["height"])
            rectangle = (
                Path()
                .move_to((x, y))
                .line_to((x + w, y))
                .line_to((x + w, y + h))
                .line_to((x, y + h))
                .close()
            )
            path.extend(rectangle)
        elif tag not in ("svg", "g", "defs", "title", "desc"):
            raise ValueError(f"SVG element {tag!r} requires native embedding.")
    return path.mapped(
        Scaling(BP_TO_MM, -BP_TO_MM) @ Translation(-layout.origin_x, -layout.origin_y),
    )
