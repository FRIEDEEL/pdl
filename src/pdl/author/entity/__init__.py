"""Drawing instances, ownership groups, selections, and drawing factories."""

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

_EXPORTS: dict[str, tuple[str, str]] = {
    "Arc": ("pdl.author.entity.factories", "Arc"),
    "Circle": ("pdl.author.entity.factories", "Circle"),
    "Entity": ("pdl.author.entity.base", "Entity"),
    "Gather": ("pdl.author.entity.gather", "Gather"),
    "Group": ("pdl.author.entity.group", "Group"),
    "Image": ("pdl.author.entity.factories", "Image"),
    "Line": ("pdl.author.entity.factories", "Line"),
    "Path": ("pdl.author.entity.factories", "Path"),
    "Polygon": ("pdl.author.entity.factories", "Polygon"),
    "Polyline": ("pdl.author.entity.factories", "Polyline"),
    "Rectangle": ("pdl.author.entity.factories", "Rectangle"),
    "TeX": ("pdl.author.entity.factories", "TeX"),
    "Text": ("pdl.author.entity.factories", "Text"),
    "frame_axes": ("pdl.author.entity.factories", "frame_axes"),
}

__all__ = [
    "Arc",
    "Circle",
    "Entity",
    "Gather",
    "Group",
    "Image",
    "Line",
    "Path",
    "Polygon",
    "Polyline",
    "Rectangle",
    "TeX",
    "Text",
    "frame_axes",
]


def __getattr__(name: str) -> object:
    """Load the explicitly requested public object without importing other layers."""
    if name not in _EXPORTS:
        raise AttributeError(name)
    module, attribute = _EXPORTS[name]
    return getattr(import_module(module), attribute)
