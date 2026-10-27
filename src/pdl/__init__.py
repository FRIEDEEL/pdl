"""Static vector drawing through a backend-independent authoring API."""

from pdl.components.connections import Connection
from pdl.components.flowchart import Decision, FlowEdge, FlowNode, Terminal
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
from pdl.media.images import Image
from pdl.rendering.config import RendererConfig
from pdl.scene.authoring import Entity
from pdl.scene.canvas import BLACK, Canvas, Color, Style
from pdl.scene.composition import Drawing, Group, bounds
from pdl.scene.gather import Gather
from pdl.scene.layers import Layer, LayerStack
from pdl.scene.paint import ColorStop, LinearGradient, RadialGradient
from pdl.scene.references import AnchorRef
from pdl.scene.resolved import Query, ResolvedGraphic
from pdl.scene.spaces import WORLD, CoordinateSystem, SpacePoint, SpaceVector
from pdl.spatial.coordinates import CoordinateSystem3D, Point3D, Transform3D, Vector3D
from pdl.spatial.curves import Cylinder, Sphere
from pdl.spatial.projection import DirectionalLight, OrthographicCamera, Scene3D
from pdl.spatial.solids import Plane3D, Polyhedron, Surface3D, regular_polyhedron
from pdl.typography.plain import Font, FontStack, Text
from pdl.typography.tex import TeX, TeXConfig

__all__ = [
    "ColorStop",
    "LinearGradient",
    "RadialGradient",
    "Image",
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


__all__ += ["FlowNode", "Decision", "Terminal", "FlowEdge"]


__all__ += [
    "CoordinateSystem3D",
    "Point3D",
    "Transform3D",
    "Vector3D",
    "DirectionalLight",
    "OrthographicCamera",
    "Scene3D",
    "Plane3D",
    "Polyhedron",
    "Surface3D",
    "regular_polyhedron",
]

__all__ += ["Cylinder", "Sphere"]
