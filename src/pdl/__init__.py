"""Static vector drawing through a backend-independent authoring API."""

from pdl.components.connections import Connection
from pdl.components.nodes import Node
from pdl.geometry.bounds import Bounds
from pdl.geometry.primitives import (
    Arc,
    Circle,
    Geometry,
    Line,
    Path,
    Point,
    Polygon,
    Polyline,
    Rectangle,
    Vector,
)
from pdl.geometry.transforms import Transform
from pdl.rendering.config import RendererConfig
from pdl.scene.authoring import Entity
from pdl.scene.canvas import BLACK, Canvas, Color, Style
from pdl.scene.composition import Drawing, Group, bounds
from pdl.scene.gather import Gather
from pdl.scene.layers import Layer, LayerStack
from pdl.scene.references import AnchorRef
from pdl.scene.resolved import Query, ResolvedGraphic
from pdl.scene.spaces import WORLD, CoordinateSystem, SpacePoint, SpaceVector
from pdl.typography.plain import Font, FontStack, Text
from pdl.typography.tex import TeX, TeXConfig

__all__ = [
    "Gather",
    "Layer",
    "LayerStack",
    "AnchorRef",
    "RendererConfig",
    "Transform",
    "Text",
    "Font",
    "FontStack",
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


__all__ += [
    "Vector",
    "Entity",
    "WORLD",
    "CoordinateSystem",
    "SpacePoint",
    "SpaceVector",
    "Query",
    "ResolvedGraphic",
]
