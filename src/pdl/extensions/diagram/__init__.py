"""Explicit public entrypoint for nodes, connections, and growing flowcharts."""

import typing as _typing
from importlib import import_module as _import_module

if _typing.TYPE_CHECKING:
    from pdl.extensions.diagram.connections import Connection as Connection
    from pdl.extensions.diagram.flowchart import Decision as Decision
    from pdl.extensions.diagram.flowchart import FlowEdge as FlowEdge
    from pdl.extensions.diagram.flowchart import FlowNode as FlowNode
    from pdl.extensions.diagram.flowchart import Terminal as Terminal
    from pdl.extensions.diagram.nodes import Node as Node

_EXPORTS: dict[str, tuple[str, str]] = {
    "Connection": ("pdl.extensions.diagram.connections", "Connection"),
    "Decision": ("pdl.extensions.diagram.flowchart", "Decision"),
    "FlowEdge": ("pdl.extensions.diagram.flowchart", "FlowEdge"),
    "FlowNode": ("pdl.extensions.diagram.flowchart", "FlowNode"),
    "Node": ("pdl.extensions.diagram.nodes", "Node"),
    "Terminal": ("pdl.extensions.diagram.flowchart", "Terminal"),
}

__all__ = [
    "Connection",
    "Decision",
    "FlowEdge",
    "FlowNode",
    "Node",
    "Terminal",
]


def __getattr__(name: str) -> object:
    """Load a public object without initializing unrelated package layers."""
    if name not in _EXPORTS:
        raise AttributeError(name)
    module, attribute = _EXPORTS[name]
    return getattr(_import_module(module), attribute)
