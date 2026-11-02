"""Pure shape and reference descriptions; these are not drawing Entities."""

from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pdl.author.geometry.bounds import Bounds as Bounds
    from pdl.author.geometry.frame import Frame as Frame
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

_EXPORTS: dict[str, tuple[str, str]] = {
    "Arc": ("pdl.author.geometry.shapes", "Arc"),
    "Bounds": ("pdl.author.geometry.bounds", "Bounds"),
    "Circle": ("pdl.author.geometry.shapes", "Circle"),
    "Frame": ("pdl.author.geometry.frame", "Frame"),
    "Line": ("pdl.author.geometry.shapes", "Line"),
    "Path": ("pdl.author.geometry.path", "Path"),
    "Point": ("pdl.author.geometry.point", "Point"),
    "Polygon": ("pdl.author.geometry.shapes", "Polygon"),
    "Polyline": ("pdl.author.geometry.shapes", "Polyline"),
    "Position": ("pdl.author.geometry.point", "Position"),
    "Rectangle": ("pdl.author.geometry.shapes", "Rectangle"),
    "Vector": ("pdl.author.geometry.point", "Vector"),
}

__all__ = [
    "Arc",
    "Bounds",
    "Circle",
    "Frame",
    "Line",
    "Path",
    "Point",
    "Polygon",
    "Polyline",
    "Position",
    "Rectangle",
    "Vector",
]


def __getattr__(name: str) -> object:
    """Load the explicitly requested public object without importing other layers."""
    if name not in _EXPORTS:
        raise AttributeError(name)
    module, attribute = _EXPORTS[name]
    return getattr(import_module(module), attribute)
