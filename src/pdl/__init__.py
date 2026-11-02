"""Everyday drawing factories, composition, paint, and Canvas."""

import typing as _typing
from importlib import import_module as _import_module

if _typing.TYPE_CHECKING:
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
    from pdl.author.style import Color as Color
    from pdl.author.style import Style as Style
    from pdl.canvas.canvas import Canvas as Canvas

_EXPORTS: dict[str, tuple[str, str]] = {
    "Canvas": ("pdl.canvas.canvas", "Canvas"),
    "Color": ("pdl.author.style", "Color"),
    "Entity": ("pdl.author.entity.base", "Entity"),
    "Gather": ("pdl.author.entity.gather", "Gather"),
    "Group": ("pdl.author.entity.group", "Group"),
    "Style": ("pdl.author.style", "Style"),
    "arc": ("pdl.author.entity.factories", "arc"),
    "circle": ("pdl.author.entity.factories", "circle"),
    "frame_axes": ("pdl.author.entity.factories", "frame_axes"),
    "image": ("pdl.author.entity.factories", "image"),
    "line": ("pdl.author.entity.factories", "line"),
    "path": ("pdl.author.entity.factories", "path"),
    "polygon": ("pdl.author.entity.factories", "polygon"),
    "polyline": ("pdl.author.entity.factories", "polyline"),
    "rectangle": ("pdl.author.entity.factories", "rectangle"),
    "tex": ("pdl.author.entity.factories", "tex"),
    "text": ("pdl.author.entity.factories", "text"),
}

__all__ = [
    "Canvas",
    "Color",
    "Entity",
    "Gather",
    "Group",
    "Style",
    "arc",
    "circle",
    "frame_axes",
    "image",
    "line",
    "path",
    "polygon",
    "polyline",
    "rectangle",
    "tex",
    "text",
]


def __getattr__(name: str) -> object:
    """Load a public object without initializing unrelated package layers."""
    if name not in _EXPORTS:
        raise AttributeError(name)
    module, attribute = _EXPORTS[name]
    return getattr(_import_module(module), attribute)
