"""Public facade; optional drawing extensions are imported only when requested."""

from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pdl.author.composition import Drawing, Group, bounds
    from pdl.author.entity import Entity
    from pdl.author.frames import Frame, ReferencePoint
    from pdl.author.gather import Gather
    from pdl.author.image import Image
    from pdl.author.layers import Layer
    from pdl.author.shapes import Arc, Circle, Line, Path, Polygon, Polyline, Rectangle
    from pdl.author.spaces import WORLD, CoordinateSystem, SpacePoint, SpaceVector
    from pdl.author.style import BLACK, Color, ColorStop, LinearGradient, RadialGradient, Style
    from pdl.author.tex import TeX
    from pdl.author.text import Text
    from pdl.canvas.canvas import Canvas
    from pdl.canvas.layers import LayerStack
    from pdl.canvas.query import Query
    from pdl.extensions.diagrams.connections import Connection
    from pdl.extensions.diagrams.flowchart import Decision, FlowEdge, FlowNode, Terminal
    from pdl.extensions.diagrams.nodes import Node
    from pdl.extensions.spatial.coordinates import (
        CoordinateSystem3D,
        Point3D,
        Transform3D,
        Vector3D,
    )
    from pdl.extensions.spatial.curves import Cylinder, Sphere
    from pdl.extensions.spatial.projected import ProjectedScene
    from pdl.extensions.spatial.projection import (
        DirectionalLight,
        OrthographicCamera,
        PerspectiveCamera,
        Scene3D,
    )
    from pdl.extensions.spatial.solids import Plane3D, Polyhedron, Surface3D, regular_polyhedron
    from pdl.extensions.spatial.surfaces import AnnularCylinder, CylinderSurface
    from pdl.foundation.geometry.bounds import Bounds
    from pdl.foundation.geometry.primitives import Geometry, Point, Vector
    from pdl.foundation.geometry.transforms import Transform
    from pdl.foundation.typography.config import RendererConfig, measurement
    from pdl.foundation.typography.shaping import Font, FontStack
    from pdl.foundation.typography.tex import TeXConfig

_EXPORTS: dict[str, tuple[str, str]] = {
    "Entity": ("pdl.author.entity", "Entity"),
    "Drawing": ("pdl.author.composition", "Drawing"),
    "Group": ("pdl.author.composition", "Group"),
    "bounds": ("pdl.author.composition", "bounds"),
    "Frame": ("pdl.author.frames", "Frame"),
    "ReferencePoint": ("pdl.author.frames", "ReferencePoint"),
    "Gather": ("pdl.author.gather", "Gather"),
    "Image": ("pdl.author.image", "Image"),
    "Layer": ("pdl.author.layers", "Layer"),
    "Arc": ("pdl.author.shapes", "Arc"),
    "Circle": ("pdl.author.shapes", "Circle"),
    "Line": ("pdl.author.shapes", "Line"),
    "Path": ("pdl.author.shapes", "Path"),
    "Polygon": ("pdl.author.shapes", "Polygon"),
    "Polyline": ("pdl.author.shapes", "Polyline"),
    "Rectangle": ("pdl.author.shapes", "Rectangle"),
    "WORLD": ("pdl.author.spaces", "WORLD"),
    "CoordinateSystem": ("pdl.author.spaces", "CoordinateSystem"),
    "SpacePoint": ("pdl.author.spaces", "SpacePoint"),
    "SpaceVector": ("pdl.author.spaces", "SpaceVector"),
    "ColorStop": ("pdl.author.style", "ColorStop"),
    "LinearGradient": ("pdl.author.style", "LinearGradient"),
    "RadialGradient": ("pdl.author.style", "RadialGradient"),
    "TeX": ("pdl.author.tex", "TeX"),
    "Text": ("pdl.author.text", "Text"),
    "BLACK": ("pdl.author.style", "BLACK"),
    "Canvas": ("pdl.canvas.canvas", "Canvas"),
    "Color": ("pdl.author.style", "Color"),
    "Style": ("pdl.author.style", "Style"),
    "LayerStack": ("pdl.canvas.layers", "LayerStack"),
    "Query": ("pdl.canvas.query", "Query"),
    "Connection": ("pdl.extensions.diagrams.connections", "Connection"),
    "Decision": ("pdl.extensions.diagrams.flowchart", "Decision"),
    "FlowEdge": ("pdl.extensions.diagrams.flowchart", "FlowEdge"),
    "FlowNode": ("pdl.extensions.diagrams.flowchart", "FlowNode"),
    "Terminal": ("pdl.extensions.diagrams.flowchart", "Terminal"),
    "Node": ("pdl.extensions.diagrams.nodes", "Node"),
    "CoordinateSystem3D": ("pdl.extensions.spatial.coordinates", "CoordinateSystem3D"),
    "Point3D": ("pdl.extensions.spatial.coordinates", "Point3D"),
    "Transform3D": ("pdl.extensions.spatial.coordinates", "Transform3D"),
    "Vector3D": ("pdl.extensions.spatial.coordinates", "Vector3D"),
    "Cylinder": ("pdl.extensions.spatial.curves", "Cylinder"),
    "Sphere": ("pdl.extensions.spatial.curves", "Sphere"),
    "ProjectedScene": ("pdl.extensions.spatial.projected", "ProjectedScene"),
    "DirectionalLight": ("pdl.extensions.spatial.projection", "DirectionalLight"),
    "OrthographicCamera": ("pdl.extensions.spatial.projection", "OrthographicCamera"),
    "PerspectiveCamera": ("pdl.extensions.spatial.projection", "PerspectiveCamera"),
    "Scene3D": ("pdl.extensions.spatial.projection", "Scene3D"),
    "Plane3D": ("pdl.extensions.spatial.solids", "Plane3D"),
    "Polyhedron": ("pdl.extensions.spatial.solids", "Polyhedron"),
    "Surface3D": ("pdl.extensions.spatial.solids", "Surface3D"),
    "regular_polyhedron": ("pdl.extensions.spatial.solids", "regular_polyhedron"),
    "AnnularCylinder": ("pdl.extensions.spatial.surfaces", "AnnularCylinder"),
    "CylinderSurface": ("pdl.extensions.spatial.surfaces", "CylinderSurface"),
    "Bounds": ("pdl.foundation.geometry.bounds", "Bounds"),
    "Geometry": ("pdl.foundation.geometry.primitives", "Geometry"),
    "Point": ("pdl.foundation.geometry.primitives", "Point"),
    "Vector": ("pdl.foundation.geometry.primitives", "Vector"),
    "Transform": ("pdl.foundation.geometry.transforms", "Transform"),
    "RendererConfig": ("pdl.foundation.typography.config", "RendererConfig"),
    "measurement": ("pdl.foundation.typography.config", "measurement"),
    "Font": ("pdl.foundation.typography.shaping", "Font"),
    "FontStack": ("pdl.foundation.typography.shaping", "FontStack"),
    "TeXConfig": ("pdl.foundation.typography.tex", "TeXConfig"),
}


def __getattr__(name: str) -> object:
    """Load public core and extension names without reverse runtime dependencies."""
    if name not in _EXPORTS:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    module, symbol = _EXPORTS[name]
    value: object = getattr(import_module(module), symbol)
    globals()[name] = value
    return value


def __dir__() -> list[str]:
    return sorted(set(globals()) | set(_EXPORTS))


__all__ = [
    "ColorStop",
    "LinearGradient",
    "RadialGradient",
    "Image",
    "Gather",
    "Layer",
    "LayerStack",
    "RendererConfig",
    "measurement",
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

__all__ += ["ProjectedScene"]

__all__ += ["PerspectiveCamera"]

__all__ += ["CylinderSurface", "AnnularCylinder"]

__all__ += ["Frame", "ReferencePoint"]
