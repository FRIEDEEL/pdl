"""Drawing factories, current geometry, and interchangeable vector exporters."""

from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pdl.author.entity.base import Entity as Entity
    from pdl.author.entity.factories import arc as arc
    from pdl.author.entity.factories import circle as circle
    from pdl.author.entity.factories import frame_axes as frame_axes
    from pdl.author.entity.factories import image as image
    from pdl.author.entity.factories import line as line
    from pdl.author.entity.factories import path as path
    from pdl.author.entity.factories import polygon as polygon
    from pdl.author.entity.factories import polyline as polyline
    from pdl.author.entity.factories import rectangle as rectangle
    from pdl.author.entity.factories import tex as tex
    from pdl.author.entity.factories import text as text
    from pdl.author.entity.gather import Gather as Gather
    from pdl.author.entity.group import Group as Group
    from pdl.author.geometry.bounds import Bounds as Bounds
    from pdl.author.geometry.frame import WORLD as WORLD
    from pdl.author.geometry.frame import CoordinateSystem as CoordinateSystem
    from pdl.author.geometry.frame import Frame as Frame
    from pdl.author.geometry.frame import SpacePoint as SpacePoint
    from pdl.author.geometry.frame import SpaceVector as SpaceVector
    from pdl.author.geometry.path import Path as PathGeometry
    from pdl.author.geometry.point import Point as Point
    from pdl.author.geometry.point import Position as Position
    from pdl.author.geometry.point import Vector as Vector
    from pdl.author.style import BLACK as BLACK
    from pdl.author.style import Color as Color
    from pdl.author.style import ColorStop as ColorStop
    from pdl.author.style import Font as Font
    from pdl.author.style import FontStack as FontStack
    from pdl.author.style import LinearGradient as LinearGradient
    from pdl.author.style import RadialGradient as RadialGradient
    from pdl.author.style import Style as Style
    from pdl.author.style.typography import RendererConfig as RendererConfig
    from pdl.author.style.typography import measurement as measurement
    from pdl.author.transform.affine import AffineTransform as AffineTransform
    from pdl.author.transform.affine import Reflection as Reflection
    from pdl.author.transform.affine import Rescale as Rescale
    from pdl.author.transform.affine import Rotation as Rotation
    from pdl.author.transform.affine import Scaling as Scaling
    from pdl.author.transform.affine import Shear as Shear
    from pdl.author.transform.affine import Translation as Translation
    from pdl.author.transform.base import Transform as Transform
    from pdl.author.util.tex import TeXConfig as TeXConfig
    from pdl.canvas.canvas import Canvas as Canvas
    from pdl.canvas.layers import Layer as Layer
    from pdl.canvas.layers import LayerStack as LayerStack
    from pdl.canvas.query import Query as Query
    from pdl.extensions.diagram.connections import Connection as Connection
    from pdl.extensions.diagram.flowchart import Decision as Decision
    from pdl.extensions.diagram.flowchart import FlowEdge as FlowEdge
    from pdl.extensions.diagram.flowchart import FlowNode as FlowNode
    from pdl.extensions.diagram.flowchart import Terminal as Terminal
    from pdl.extensions.diagram.nodes import Node as Node
    from pdl.extensions.spatial.coordinates import CoordinateSystem3D as CoordinateSystem3D
    from pdl.extensions.spatial.coordinates import Point3D as Point3D
    from pdl.extensions.spatial.coordinates import Transform3D as Transform3D
    from pdl.extensions.spatial.coordinates import Vector3D as Vector3D
    from pdl.extensions.spatial.curves import Cylinder as Cylinder
    from pdl.extensions.spatial.curves import Sphere as Sphere
    from pdl.extensions.spatial.projected import ProjectedScene as ProjectedScene
    from pdl.extensions.spatial.projection import DirectionalLight as DirectionalLight
    from pdl.extensions.spatial.projection import OrthographicCamera as OrthographicCamera
    from pdl.extensions.spatial.projection import PerspectiveCamera as PerspectiveCamera
    from pdl.extensions.spatial.projection import Scene3D as Scene3D
    from pdl.extensions.spatial.solids import Plane3D as Plane3D
    from pdl.extensions.spatial.solids import Polyhedron as Polyhedron
    from pdl.extensions.spatial.solids import Surface3D as Surface3D
    from pdl.extensions.spatial.solids import regular_polyhedron as regular_polyhedron
    from pdl.extensions.spatial.surfaces import AnnularCylinder as AnnularCylinder
    from pdl.extensions.spatial.surfaces import CylinderSurface as CylinderSurface

_EXPORTS: dict[str, tuple[str, str]] = {
    "AffineTransform": ("pdl.author.transform.affine", "AffineTransform"),
    "AnnularCylinder": ("pdl.extensions.spatial.surfaces", "AnnularCylinder"),
    "arc": ("pdl.author.entity.factories", "arc"),
    "BLACK": ("pdl.author.style", "BLACK"),
    "Bounds": ("pdl.author.geometry.bounds", "Bounds"),
    "Canvas": ("pdl.canvas.canvas", "Canvas"),
    "circle": ("pdl.author.entity.factories", "circle"),
    "Color": ("pdl.author.style", "Color"),
    "ColorStop": ("pdl.author.style", "ColorStop"),
    "Connection": ("pdl.extensions.diagram.connections", "Connection"),
    "CoordinateSystem": ("pdl.author.geometry.frame", "CoordinateSystem"),
    "CoordinateSystem3D": ("pdl.extensions.spatial.coordinates", "CoordinateSystem3D"),
    "Cylinder": ("pdl.extensions.spatial.curves", "Cylinder"),
    "CylinderSurface": ("pdl.extensions.spatial.surfaces", "CylinderSurface"),
    "Decision": ("pdl.extensions.diagram.flowchart", "Decision"),
    "DirectionalLight": ("pdl.extensions.spatial.projection", "DirectionalLight"),
    "Entity": ("pdl.author.entity.base", "Entity"),
    "FlowEdge": ("pdl.extensions.diagram.flowchart", "FlowEdge"),
    "FlowNode": ("pdl.extensions.diagram.flowchart", "FlowNode"),
    "Font": ("pdl.author.style", "Font"),
    "FontStack": ("pdl.author.style", "FontStack"),
    "Frame": ("pdl.author.geometry.frame", "Frame"),
    "Gather": ("pdl.author.entity.gather", "Gather"),
    "Group": ("pdl.author.entity.group", "Group"),
    "image": ("pdl.author.entity.factories", "image"),
    "Layer": ("pdl.canvas.layers", "Layer"),
    "LayerStack": ("pdl.canvas.layers", "LayerStack"),
    "line": ("pdl.author.entity.factories", "line"),
    "LinearGradient": ("pdl.author.style", "LinearGradient"),
    "Node": ("pdl.extensions.diagram.nodes", "Node"),
    "OrthographicCamera": ("pdl.extensions.spatial.projection", "OrthographicCamera"),
    "path": ("pdl.author.entity.factories", "path"),
    "PathGeometry": ("pdl.author.geometry.path", "Path"),
    "PerspectiveCamera": ("pdl.extensions.spatial.projection", "PerspectiveCamera"),
    "Plane3D": ("pdl.extensions.spatial.solids", "Plane3D"),
    "Point": ("pdl.author.geometry.point", "Point"),
    "Point3D": ("pdl.extensions.spatial.coordinates", "Point3D"),
    "polygon": ("pdl.author.entity.factories", "polygon"),
    "Polyhedron": ("pdl.extensions.spatial.solids", "Polyhedron"),
    "polyline": ("pdl.author.entity.factories", "polyline"),
    "Position": ("pdl.author.geometry.point", "Position"),
    "ProjectedScene": ("pdl.extensions.spatial.projected", "ProjectedScene"),
    "Query": ("pdl.canvas.query", "Query"),
    "RadialGradient": ("pdl.author.style", "RadialGradient"),
    "rectangle": ("pdl.author.entity.factories", "rectangle"),
    "Reflection": ("pdl.author.transform.affine", "Reflection"),
    "RendererConfig": ("pdl.author.style.typography", "RendererConfig"),
    "Rescale": ("pdl.author.transform.affine", "Rescale"),
    "Rotation": ("pdl.author.transform.affine", "Rotation"),
    "Scaling": ("pdl.author.transform.affine", "Scaling"),
    "Scene3D": ("pdl.extensions.spatial.projection", "Scene3D"),
    "Shear": ("pdl.author.transform.affine", "Shear"),
    "SpacePoint": ("pdl.author.geometry.frame", "SpacePoint"),
    "SpaceVector": ("pdl.author.geometry.frame", "SpaceVector"),
    "Sphere": ("pdl.extensions.spatial.curves", "Sphere"),
    "Style": ("pdl.author.style", "Style"),
    "Surface3D": ("pdl.extensions.spatial.solids", "Surface3D"),
    "tex": ("pdl.author.entity.factories", "tex"),
    "TeXConfig": ("pdl.author.util.tex", "TeXConfig"),
    "Terminal": ("pdl.extensions.diagram.flowchart", "Terminal"),
    "text": ("pdl.author.entity.factories", "text"),
    "Transform": ("pdl.author.transform.base", "Transform"),
    "Transform3D": ("pdl.extensions.spatial.coordinates", "Transform3D"),
    "Translation": ("pdl.author.transform.affine", "Translation"),
    "Vector": ("pdl.author.geometry.point", "Vector"),
    "Vector3D": ("pdl.extensions.spatial.coordinates", "Vector3D"),
    "WORLD": ("pdl.author.geometry.frame", "WORLD"),
    "frame_axes": ("pdl.author.entity.factories", "frame_axes"),
    "measurement": ("pdl.author.style.typography", "measurement"),
    "regular_polyhedron": ("pdl.extensions.spatial.solids", "regular_polyhedron"),
}

__all__ = [
    "AffineTransform",
    "AnnularCylinder",
    "arc",
    "BLACK",
    "Bounds",
    "Canvas",
    "circle",
    "Color",
    "ColorStop",
    "Connection",
    "CoordinateSystem",
    "CoordinateSystem3D",
    "Cylinder",
    "CylinderSurface",
    "Decision",
    "DirectionalLight",
    "Entity",
    "FlowEdge",
    "FlowNode",
    "Font",
    "FontStack",
    "Frame",
    "Gather",
    "Group",
    "image",
    "Layer",
    "LayerStack",
    "line",
    "LinearGradient",
    "Node",
    "OrthographicCamera",
    "path",
    "PathGeometry",
    "PerspectiveCamera",
    "Plane3D",
    "Point",
    "Point3D",
    "polygon",
    "Polyhedron",
    "polyline",
    "Position",
    "ProjectedScene",
    "Query",
    "RadialGradient",
    "rectangle",
    "Reflection",
    "RendererConfig",
    "Rescale",
    "Rotation",
    "Scaling",
    "Scene3D",
    "Shear",
    "SpacePoint",
    "SpaceVector",
    "Sphere",
    "Style",
    "Surface3D",
    "tex",
    "TeXConfig",
    "Terminal",
    "text",
    "Transform",
    "Transform3D",
    "Translation",
    "Vector",
    "Vector3D",
    "WORLD",
    "frame_axes",
    "measurement",
    "regular_polyhedron",
]


def __getattr__(name: str) -> object:
    """Load the explicitly requested public object without importing other layers."""
    if name not in _EXPORTS:
        raise AttributeError(name)
    module, attribute = _EXPORTS[name]
    return getattr(import_module(module), attribute)
