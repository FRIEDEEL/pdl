"""Pure shape and frame descriptions for explicit geometric construction."""

import typing as _typing
from importlib import import_module as _import_module

if _typing.TYPE_CHECKING:
    from pdl.author.geometry.bounds import Bounds as Bounds
    from pdl.author.geometry.frame import WORLD as WORLD
    from pdl.author.geometry.frame import CoordinateSystem as CoordinateSystem
    from pdl.author.geometry.frame import Frame as Frame
    from pdl.author.geometry.frame import SpacePoint as SpacePoint
    from pdl.author.geometry.frame import SpaceVector as SpaceVector
    from pdl.author.geometry.image import Image as Image
    from pdl.author.geometry.path import Path as Path
    from pdl.author.geometry.point import Point as Point
    from pdl.author.geometry.point import Position as Position
    from pdl.author.geometry.point import Vector as Vector
    from pdl.author.geometry.shapes import Arc as Arc
    from pdl.author.geometry.shapes import Circle as Circle
    from pdl.author.geometry.shapes import Line as Line
    from pdl.author.geometry.shapes import Polygon as Polygon
    from pdl.author.geometry.shapes import Polyline as Polyline
    from pdl.author.geometry.shapes import Rectangle as Rectangle
    from pdl.author.geometry.tex import TeX as TeX
    from pdl.author.geometry.text import Text as Text

_EXPORTS: dict[str, tuple[str, str]] = {
    "Arc": ("pdl.author.geometry.shapes", "Arc"),
    "Bounds": ("pdl.author.geometry.bounds", "Bounds"),
    "Circle": ("pdl.author.geometry.shapes", "Circle"),
    "CoordinateSystem": ("pdl.author.geometry.frame", "CoordinateSystem"),
    "Frame": ("pdl.author.geometry.frame", "Frame"),
    "Image": ("pdl.author.geometry.image", "Image"),
    "Line": ("pdl.author.geometry.shapes", "Line"),
    "Path": ("pdl.author.geometry.path", "Path"),
    "Point": ("pdl.author.geometry.point", "Point"),
    "Polygon": ("pdl.author.geometry.shapes", "Polygon"),
    "Polyline": ("pdl.author.geometry.shapes", "Polyline"),
    "Position": ("pdl.author.geometry.point", "Position"),
    "Rectangle": ("pdl.author.geometry.shapes", "Rectangle"),
    "SpacePoint": ("pdl.author.geometry.frame", "SpacePoint"),
    "SpaceVector": ("pdl.author.geometry.frame", "SpaceVector"),
    "TeX": ("pdl.author.geometry.tex", "TeX"),
    "Text": ("pdl.author.geometry.text", "Text"),
    "Vector": ("pdl.author.geometry.point", "Vector"),
    "WORLD": ("pdl.author.geometry.frame", "WORLD"),
}

__all__ = [
    "Arc",
    "Bounds",
    "Circle",
    "CoordinateSystem",
    "Frame",
    "Image",
    "Line",
    "Path",
    "Point",
    "Polygon",
    "Polyline",
    "Position",
    "Rectangle",
    "SpacePoint",
    "SpaceVector",
    "TeX",
    "Text",
    "Vector",
    "WORLD",
]


def __getattr__(name: str) -> object:
    """Load a public object without initializing unrelated package layers."""
    if name not in _EXPORTS:
        raise AttributeError(name)
    module, attribute = _EXPORTS[name]
    return getattr(_import_module(module), attribute)
