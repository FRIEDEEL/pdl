"""Canvas, layer ordering, numerical queries, and viewport records."""

import typing as _typing
from importlib import import_module as _import_module

if _typing.TYPE_CHECKING:
    from pdl.canvas.canvas import Canvas as Canvas
    from pdl.canvas.layers import Layer as Layer
    from pdl.canvas.layers import LayerStack as LayerStack
    from pdl.canvas.query import Query as Query
    from pdl.canvas.records import Page as Page
    from pdl.canvas.records import Viewport as Viewport

_EXPORTS: dict[str, tuple[str, str]] = {
    "Canvas": ("pdl.canvas.canvas", "Canvas"),
    "Layer": ("pdl.canvas.layers", "Layer"),
    "LayerStack": ("pdl.canvas.layers", "LayerStack"),
    "Page": ("pdl.canvas.records", "Page"),
    "Query": ("pdl.canvas.query", "Query"),
    "Viewport": ("pdl.canvas.records", "Viewport"),
}

__all__ = [
    "Canvas",
    "Layer",
    "LayerStack",
    "Page",
    "Query",
    "Viewport",
]


def __getattr__(name: str) -> object:
    """Load a public object without initializing unrelated package layers."""
    if name not in _EXPORTS:
        raise AttributeError(name)
    module, attribute = _EXPORTS[name]
    return getattr(_import_module(module), attribute)
