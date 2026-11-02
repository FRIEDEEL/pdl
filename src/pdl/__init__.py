"""Drawing factories, current geometry, and interchangeable vector exporters."""

from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pdl.author.entity.base import Entity as Entity
    from pdl.author.entity.factories import Arc as Arc
    from pdl.author.entity.factories import Circle as Circle
    from pdl.author.entity.factories import Image as Image
    from pdl.author.entity.factories import Line as Line
    from pdl.author.entity.factories import Path as Path
    from pdl.author.entity.factories import Polygon as Polygon
    from pdl.author.entity.factories import Polyline as Polyline
    from pdl.author.entity.factories import Rectangle as Rectangle
    from pdl.author.entity.factories import TeX as TeX
    from pdl.author.entity.factories import Text as Text
    from pdl.author.entity.factories import frame_axes as frame_axes
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
    from pdl.extensions.spacial.coordinates import CoordinateSystem3D as CoordinateSystem3D
    from pdl.extensions.spacial.coordinates import Point3D as Point3D
    from pdl.extensions.spacial.coordinates import Transform3D as Transform3D
    from pdl.extensions.spacial.coordinates import Vector3D as Vector3D
    from pdl.extensions.spacial.curves import Cylinder as Cylinder
    from pdl.extensions.spacial.curves import Sphere as Sphere
    from pdl.extensions.spacial.projected import ProjectedScene as ProjectedScene
    from pdl.extensions.spacial.projection import DirectionalLight as DirectionalLight
    from pdl.extensions.spacial.projection import OrthographicCamera as OrthographicCamera
    from pdl.extensions.spacial.projection import PerspectiveCamera as PerspectiveCamera
    from pdl.extensions.spacial.projection import Scene3D as Scene3D
    from pdl.extensions.spacial.solids import Plane3D as Plane3D
    from pdl.extensions.spacial.solids import Polyhedron as Polyhedron
    from pdl.extensions.spacial.solids import Surface3D as Surface3D
    from pdl.extensions.spacial.solids import regular_polyhedron as regular_polyhedron
    from pdl.extensions.spacial.surfaces import AnnularCylinder as AnnularCylinder
    from pdl.extensions.spacial.surfaces import CylinderSurface as CylinderSurface

_EXPORTS: dict[str, tuple[str, str]] = {
    "AffineTransform": ("pdl.author.transform.affine", "AffineTransform"),
    "AnnularCylinder": ("pdl.extensions.spacial.surfaces", "AnnularCylinder"),
    "Arc": ("pdl.author.entity.factories", "Arc"),
    "BLACK": ("pdl.author.style", "BLACK"),
    "Bounds": ("pdl.author.geometry.bounds", "Bounds"),
    "Canvas": ("pdl.canvas.canvas", "Canvas"),
    "Circle": ("pdl.author.entity.factories", "Circle"),
    "Color": ("pdl.author.style", "Color"),
    "ColorStop": ("pdl.author.style", "ColorStop"),
    "Connection": ("pdl.extensions.diagram.connections", "Connection"),
    "CoordinateSystem": ("pdl.author.geometry.frame", "CoordinateSystem"),
    "CoordinateSystem3D": ("pdl.extensions.spacial.coordinates", "CoordinateSystem3D"),
    "Cylinder": ("pdl.extensions.spacial.curves", "Cylinder"),
    "CylinderSurface": ("pdl.extensions.spacial.surfaces", "CylinderSurface"),
    "Decision": ("pdl.extensions.diagram.flowchart", "Decision"),
    "DirectionalLight": ("pdl.extensions.spacial.projection", "DirectionalLight"),
    "Entity": ("pdl.author.entity.base", "Entity"),
    "FlowEdge": ("pdl.extensions.diagram.flowchart", "FlowEdge"),
    "FlowNode": ("pdl.extensions.diagram.flowchart", "FlowNode"),
    "Font": ("pdl.author.style", "Font"),
    "FontStack": ("pdl.author.style", "FontStack"),
    "Frame": ("pdl.author.geometry.frame", "Frame"),
    "Gather": ("pdl.author.entity.gather", "Gather"),
    "Group": ("pdl.author.entity.group", "Group"),
    "Image": ("pdl.author.entity.factories", "Image"),
    "Layer": ("pdl.canvas.layers", "Layer"),
    "LayerStack": ("pdl.canvas.layers", "LayerStack"),
    "Line": ("pdl.author.entity.factories", "Line"),
    "LinearGradient": ("pdl.author.style", "LinearGradient"),
    "Node": ("pdl.extensions.diagram.nodes", "Node"),
    "OrthographicCamera": ("pdl.extensions.spacial.projection", "OrthographicCamera"),
    "Path": ("pdl.author.entity.factories", "Path"),
    "PathGeometry": ("pdl.author.geometry.path", "Path"),
    "PerspectiveCamera": ("pdl.extensions.spacial.projection", "PerspectiveCamera"),
    "Plane3D": ("pdl.extensions.spacial.solids", "Plane3D"),
    "Point": ("pdl.author.geometry.point", "Point"),
    "Point3D": ("pdl.extensions.spacial.coordinates", "Point3D"),
    "Polygon": ("pdl.author.entity.factories", "Polygon"),
    "Polyhedron": ("pdl.extensions.spacial.solids", "Polyhedron"),
    "Polyline": ("pdl.author.entity.factories", "Polyline"),
    "Position": ("pdl.author.geometry.point", "Position"),
    "ProjectedScene": ("pdl.extensions.spacial.projected", "ProjectedScene"),
    "Query": ("pdl.canvas.query", "Query"),
    "RadialGradient": ("pdl.author.style", "RadialGradient"),
    "Rectangle": ("pdl.author.entity.factories", "Rectangle"),
    "Reflection": ("pdl.author.transform.affine", "Reflection"),
    "RendererConfig": ("pdl.author.style.typography", "RendererConfig"),
    "Rescale": ("pdl.author.transform.affine", "Rescale"),
    "Rotation": ("pdl.author.transform.affine", "Rotation"),
    "Scaling": ("pdl.author.transform.affine", "Scaling"),
    "Scene3D": ("pdl.extensions.spacial.projection", "Scene3D"),
    "Shear": ("pdl.author.transform.affine", "Shear"),
    "SpacePoint": ("pdl.author.geometry.frame", "SpacePoint"),
    "SpaceVector": ("pdl.author.geometry.frame", "SpaceVector"),
    "Sphere": ("pdl.extensions.spacial.curves", "Sphere"),
    "Style": ("pdl.author.style", "Style"),
    "Surface3D": ("pdl.extensions.spacial.solids", "Surface3D"),
    "TeX": ("pdl.author.entity.factories", "TeX"),
    "TeXConfig": ("pdl.author.util.tex", "TeXConfig"),
    "Terminal": ("pdl.extensions.diagram.flowchart", "Terminal"),
    "Text": ("pdl.author.entity.factories", "Text"),
    "Transform": ("pdl.author.transform.base", "Transform"),
    "Transform3D": ("pdl.extensions.spacial.coordinates", "Transform3D"),
    "Translation": ("pdl.author.transform.affine", "Translation"),
    "Vector": ("pdl.author.geometry.point", "Vector"),
    "Vector3D": ("pdl.extensions.spacial.coordinates", "Vector3D"),
    "WORLD": ("pdl.author.geometry.frame", "WORLD"),
    "frame_axes": ("pdl.author.entity.factories", "frame_axes"),
    "measurement": ("pdl.author.style.typography", "measurement"),
    "regular_polyhedron": ("pdl.extensions.spacial.solids", "regular_polyhedron"),
}

__all__ = [
    "AffineTransform",
    "AnnularCylinder",
    "Arc",
    "BLACK",
    "Bounds",
    "Canvas",
    "Circle",
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
    "Image",
    "Layer",
    "LayerStack",
    "Line",
    "LinearGradient",
    "Node",
    "OrthographicCamera",
    "Path",
    "PathGeometry",
    "PerspectiveCamera",
    "Plane3D",
    "Point",
    "Point3D",
    "Polygon",
    "Polyhedron",
    "Polyline",
    "Position",
    "ProjectedScene",
    "Query",
    "RadialGradient",
    "Rectangle",
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
    "TeX",
    "TeXConfig",
    "Terminal",
    "Text",
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
