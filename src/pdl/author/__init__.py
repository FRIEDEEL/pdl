"""The sole editable drawing domain, independent of Canvas and output adapters."""

from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pdl.author.entity import Arc as Arc
    from pdl.author.entity import Circle as Circle
    from pdl.author.entity import Entity as Entity
    from pdl.author.entity import Gather as Gather
    from pdl.author.entity import Group as Group
    from pdl.author.entity import Image as Image
    from pdl.author.entity import Line as Line
    from pdl.author.entity import Path as Path
    from pdl.author.entity import Polygon as Polygon
    from pdl.author.entity import Polyline as Polyline
    from pdl.author.entity import Rectangle as Rectangle
    from pdl.author.entity import TeX as TeX
    from pdl.author.entity import Text as Text
    from pdl.author.entity import frame_axes as frame_axes
    from pdl.author.style import BLACK as BLACK
    from pdl.author.style import Color as Color
    from pdl.author.style import ColorStop as ColorStop
    from pdl.author.style import Font as Font
    from pdl.author.style import FontStack as FontStack
    from pdl.author.style import LinearGradient as LinearGradient
    from pdl.author.style import RadialGradient as RadialGradient
    from pdl.author.style import Style as Style

_EXPORTS: dict[str, tuple[str, str]] = {
    "Arc": ("pdl.author.entity", "Arc"),
    "BLACK": ("pdl.author.style", "BLACK"),
    "Circle": ("pdl.author.entity", "Circle"),
    "Color": ("pdl.author.style", "Color"),
    "ColorStop": ("pdl.author.style", "ColorStop"),
    "Entity": ("pdl.author.entity", "Entity"),
    "Font": ("pdl.author.style", "Font"),
    "FontStack": ("pdl.author.style", "FontStack"),
    "Gather": ("pdl.author.entity", "Gather"),
    "Group": ("pdl.author.entity", "Group"),
    "Image": ("pdl.author.entity", "Image"),
    "Line": ("pdl.author.entity", "Line"),
    "LinearGradient": ("pdl.author.style", "LinearGradient"),
    "Path": ("pdl.author.entity", "Path"),
    "Polygon": ("pdl.author.entity", "Polygon"),
    "Polyline": ("pdl.author.entity", "Polyline"),
    "RadialGradient": ("pdl.author.style", "RadialGradient"),
    "Rectangle": ("pdl.author.entity", "Rectangle"),
    "Style": ("pdl.author.style", "Style"),
    "TeX": ("pdl.author.entity", "TeX"),
    "Text": ("pdl.author.entity", "Text"),
    "frame_axes": ("pdl.author.entity", "frame_axes"),
}

__all__ = [
    "Arc",
    "BLACK",
    "Circle",
    "Color",
    "ColorStop",
    "Entity",
    "Font",
    "FontStack",
    "Gather",
    "Group",
    "Image",
    "Line",
    "LinearGradient",
    "Path",
    "Polygon",
    "Polyline",
    "RadialGradient",
    "Rectangle",
    "Style",
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
