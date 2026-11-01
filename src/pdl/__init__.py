"""Drawing factories, current geometry, and interchangeable vector exporters."""

from pdl.author.entity.base import Entity as Entity
from pdl.author.entity.factories import (
    Arc as Arc,
)
from pdl.author.entity.factories import (
    Circle as Circle,
)
from pdl.author.entity.factories import (
    Image as Image,
)
from pdl.author.entity.factories import (
    Line as Line,
)
from pdl.author.entity.factories import (
    Path as Path,
)
from pdl.author.entity.factories import (
    Polygon as Polygon,
)
from pdl.author.entity.factories import (
    Polyline as Polyline,
)
from pdl.author.entity.factories import (
    Rectangle as Rectangle,
)
from pdl.author.entity.factories import (
    TeX as TeX,
)
from pdl.author.entity.factories import (
    Text as Text,
)
from pdl.author.entity.factories import (
    frame_axes as frame_axes,
)
from pdl.author.entity.gather import Gather as Gather
from pdl.author.entity.group import Group as Group
from pdl.author.geometry.bounds import Bounds as Bounds
from pdl.author.geometry.frame import (
    WORLD as WORLD,
)
from pdl.author.geometry.frame import (
    CoordinateSystem as CoordinateSystem,
)
from pdl.author.geometry.frame import (
    Frame as Frame,
)
from pdl.author.geometry.frame import (
    SpacePoint as SpacePoint,
)
from pdl.author.geometry.frame import (
    SpaceVector as SpaceVector,
)
from pdl.author.geometry.path import Path as PathGeometry
from pdl.author.geometry.point import Point as Point
from pdl.author.geometry.point import Position as Position
from pdl.author.geometry.point import Vector as Vector
from pdl.author.style import (
    BLACK as BLACK,
)
from pdl.author.style import (
    Color as Color,
)
from pdl.author.style import (
    ColorStop as ColorStop,
)
from pdl.author.style import (
    Font as Font,
)
from pdl.author.style import (
    FontStack as FontStack,
)
from pdl.author.style import (
    LinearGradient as LinearGradient,
)
from pdl.author.style import (
    RadialGradient as RadialGradient,
)
from pdl.author.style import (
    Style as Style,
)
from pdl.author.style.typography import RendererConfig as RendererConfig
from pdl.author.style.typography import measurement as measurement
from pdl.author.transform.affine import (
    AffineTransform as AffineTransform,
)
from pdl.author.transform.affine import (
    Reflection as Reflection,
)
from pdl.author.transform.affine import (
    Rescale as Rescale,
)
from pdl.author.transform.affine import (
    Rotation as Rotation,
)
from pdl.author.transform.affine import (
    Scaling as Scaling,
)
from pdl.author.transform.affine import (
    Shear as Shear,
)
from pdl.author.transform.affine import (
    Translation as Translation,
)
from pdl.author.transform.base import Transform as Transform
from pdl.author.util.tex import TeXConfig as TeXConfig
from pdl.canvas.canvas import Canvas as Canvas
from pdl.canvas.layers import Layer as Layer
from pdl.canvas.layers import LayerStack as LayerStack
from pdl.canvas.query import Query as Query

__all__ = ["PathGeometry"]


# Optional extensions are loaded only through this explicit public facade.
from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pdl.extensions.spacial.coordinates import (
        CoordinateSystem3D as CoordinateSystem3D,
    )
    from pdl.extensions.spacial.coordinates import (
        Point3D as Point3D,
    )
    from pdl.extensions.spacial.coordinates import (
        Transform3D as Transform3D,
    )
    from pdl.extensions.spacial.coordinates import (
        Vector3D as Vector3D,
    )
    from pdl.extensions.spacial.curves import Cylinder as Cylinder
    from pdl.extensions.spacial.curves import Sphere as Sphere
    from pdl.extensions.spacial.projected import ProjectedScene as ProjectedScene
    from pdl.extensions.spacial.projection import (
        DirectionalLight as DirectionalLight,
    )
    from pdl.extensions.spacial.projection import (
        OrthographicCamera as OrthographicCamera,
    )
    from pdl.extensions.spacial.projection import (
        PerspectiveCamera as PerspectiveCamera,
    )
    from pdl.extensions.spacial.projection import (
        Scene3D as Scene3D,
    )
    from pdl.extensions.spacial.solids import (
        Plane3D as Plane3D,
    )
    from pdl.extensions.spacial.solids import (
        Polyhedron as Polyhedron,
    )
    from pdl.extensions.spacial.solids import (
        Surface3D as Surface3D,
    )
    from pdl.extensions.spacial.solids import (
        regular_polyhedron as regular_polyhedron,
    )
    from pdl.extensions.spacial.surfaces import (
        AnnularCylinder as AnnularCylinder,
    )
    from pdl.extensions.spacial.surfaces import (
        CylinderSurface as CylinderSurface,
    )

_EXTENSIONS = {
    name: "pdl.extensions.spacial." + module
    for module, names in (
        ("coordinates", ("Point3D", "Vector3D", "Transform3D", "CoordinateSystem3D")),
        ("curves", ("Sphere", "Cylinder")),
        ("projection", ("Scene3D", "OrthographicCamera", "PerspectiveCamera", "DirectionalLight")),
        ("projected", ("ProjectedScene",)),
        ("solids", ("Plane3D", "Polyhedron", "Surface3D", "regular_polyhedron")),
        ("surfaces", ("CylinderSurface", "AnnularCylinder")),
    )
    for name in names
}


def __getattr__(name: str) -> object:
    if name not in _EXTENSIONS:
        raise AttributeError(name)
    return getattr(import_module(_EXTENSIONS[name]), name)
