"""Static vector drawing through a backend-independent authoring API."""

from pdl.bounds import Bounds
from pdl.canvas import BLACK, Canvas, Color, Style
from pdl.connections import Connection
from pdl.geometry import (
    Arc,
    Circle,
    Geometry,
    Line,
    Path,
    Point,
    Polygon,
    Polyline,
    Rectangle,
)
from pdl.nodes import Node
from pdl.scene import Drawing, Group, bounds
from pdl.tex import TeX, TeXConfig
from pdl.text import Font, Text
from pdl.transforms import Transform

__all__ = [
    "Transform",
    "Text",
    "Font",
    "TeXConfig",
    "TeX",
    "bounds",
    "Group",
    "Drawing",
    "Node",
    "Connection",
    "Bounds",
    "BLACK",
    "Arc",
    "Canvas",
    "Circle",
    "Color",
    "Geometry",
    "Line",
    "Path",
    "Point",
    "Polygon",
    "Polyline",
    "Rectangle",
    "Style",
]
