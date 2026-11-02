"""The sole editable drawing domain, independent of Canvas and output adapters."""

from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pdl.author.entity import Entity as Entity
    from pdl.author.entity import Gather as Gather
    from pdl.author.entity import Group as Group
    from pdl.author.entity import arc as arc
    from pdl.author.entity import circle as circle
    from pdl.author.entity import frame_axes as frame_axes
    from pdl.author.entity import image as image
    from pdl.author.entity import line as line
    from pdl.author.entity import path as path
    from pdl.author.entity import polygon as polygon
    from pdl.author.entity import polyline as polyline
    from pdl.author.entity import rectangle as rectangle
    from pdl.author.entity import tex as tex
    from pdl.author.entity import text as text
    from pdl.author.style import BLACK as BLACK
    from pdl.author.style import Color as Color
    from pdl.author.style import ColorStop as ColorStop
    from pdl.author.style import Font as Font
    from pdl.author.style import FontStack as FontStack
    from pdl.author.style import LinearGradient as LinearGradient
    from pdl.author.style import RadialGradient as RadialGradient
    from pdl.author.style import Style as Style

_EXPORTS: dict[str, tuple[str, str]] = {
    "arc": ("pdl.author.entity", "arc"),
    "BLACK": ("pdl.author.style", "BLACK"),
    "circle": ("pdl.author.entity", "circle"),
    "Color": ("pdl.author.style", "Color"),
    "ColorStop": ("pdl.author.style", "ColorStop"),
    "Entity": ("pdl.author.entity", "Entity"),
    "Font": ("pdl.author.style", "Font"),
    "FontStack": ("pdl.author.style", "FontStack"),
    "Gather": ("pdl.author.entity", "Gather"),
    "Group": ("pdl.author.entity", "Group"),
    "image": ("pdl.author.entity", "image"),
    "line": ("pdl.author.entity", "line"),
    "LinearGradient": ("pdl.author.style", "LinearGradient"),
    "path": ("pdl.author.entity", "path"),
    "polygon": ("pdl.author.entity", "polygon"),
    "polyline": ("pdl.author.entity", "polyline"),
    "RadialGradient": ("pdl.author.style", "RadialGradient"),
    "rectangle": ("pdl.author.entity", "rectangle"),
    "Style": ("pdl.author.style", "Style"),
    "tex": ("pdl.author.entity", "tex"),
    "text": ("pdl.author.entity", "text"),
    "frame_axes": ("pdl.author.entity", "frame_axes"),
}

__all__ = [
    "arc",
    "BLACK",
    "circle",
    "Color",
    "ColorStop",
    "Entity",
    "Font",
    "FontStack",
    "Gather",
    "Group",
    "image",
    "line",
    "LinearGradient",
    "path",
    "polygon",
    "polyline",
    "RadialGradient",
    "rectangle",
    "Style",
    "tex",
    "text",
    "frame_axes",
]


def __getattr__(name: str) -> object:
    """Load the explicitly requested public object without importing other layers."""
    if name not in _EXPORTS:
        raise AttributeError(name)
    module, attribute = _EXPORTS[name]
    return getattr(import_module(module), attribute)
