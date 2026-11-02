"""Explicit public entrypoint for 3D shapes, projection, cameras, and visibility."""

import typing as _typing
from importlib import import_module as _import_module

if _typing.TYPE_CHECKING:
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
    "AnnularCylinder": ("pdl.extensions.spatial.surfaces", "AnnularCylinder"),
    "CoordinateSystem3D": ("pdl.extensions.spatial.coordinates", "CoordinateSystem3D"),
    "Cylinder": ("pdl.extensions.spatial.curves", "Cylinder"),
    "CylinderSurface": ("pdl.extensions.spatial.surfaces", "CylinderSurface"),
    "DirectionalLight": ("pdl.extensions.spatial.projection", "DirectionalLight"),
    "OrthographicCamera": ("pdl.extensions.spatial.projection", "OrthographicCamera"),
    "PerspectiveCamera": ("pdl.extensions.spatial.projection", "PerspectiveCamera"),
    "Plane3D": ("pdl.extensions.spatial.solids", "Plane3D"),
    "Point3D": ("pdl.extensions.spatial.coordinates", "Point3D"),
    "Polyhedron": ("pdl.extensions.spatial.solids", "Polyhedron"),
    "ProjectedScene": ("pdl.extensions.spatial.projected", "ProjectedScene"),
    "Scene3D": ("pdl.extensions.spatial.projection", "Scene3D"),
    "Sphere": ("pdl.extensions.spatial.curves", "Sphere"),
    "Surface3D": ("pdl.extensions.spatial.solids", "Surface3D"),
    "Transform3D": ("pdl.extensions.spatial.coordinates", "Transform3D"),
    "Vector3D": ("pdl.extensions.spatial.coordinates", "Vector3D"),
    "regular_polyhedron": ("pdl.extensions.spatial.solids", "regular_polyhedron"),
}

__all__ = [
    "AnnularCylinder",
    "CoordinateSystem3D",
    "Cylinder",
    "CylinderSurface",
    "DirectionalLight",
    "OrthographicCamera",
    "PerspectiveCamera",
    "Plane3D",
    "Point3D",
    "Polyhedron",
    "ProjectedScene",
    "Scene3D",
    "Sphere",
    "Surface3D",
    "Transform3D",
    "Vector3D",
    "regular_polyhedron",
]


def __getattr__(name: str) -> object:
    """Load a public object without initializing unrelated package layers."""
    if name not in _EXPORTS:
        raise AttributeError(name)
    module, attribute = _EXPORTS[name]
    return getattr(_import_module(module), attribute)
