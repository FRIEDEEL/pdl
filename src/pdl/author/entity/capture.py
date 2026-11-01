"""State capture into the same Author Entity model used for editing."""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from typing import Protocol, runtime_checkable

from pdl.author.entity.base import Entity
from pdl.author.entity.group import Group
from pdl.author.geometry.tex import TeX
from pdl.author.geometry.text import Text
from pdl.author.style.font import FontStack


@runtime_checkable
class Composite(Protocol):
    """Extension hook: expand into core Author entities before rendering."""

    def decompose(self) -> tuple[Entity, ...]: ...


def freeze(value: Entity | Composite) -> Entity:
    """Capture state, effective styles, and typography without a second model."""
    return _freeze(value, frozenset())


def _freeze(value: object, ancestors: frozenset[int]) -> Entity:
    if id(value) in ancestors:
        raise ValueError("Cyclic composite graph during capture.")
    ancestors = ancestors | {id(value)}
    if isinstance(value, Group):
        result = Group(
            *(_freeze(m, ancestors) for m in value.members),
            style=value.effective_style,
            reference=value.reference,
        )
        return result
    if isinstance(value, Composite):
        children = tuple(_freeze(m, ancestors) for m in value.decompose())
        return Group(*children, style=value.effective_style if isinstance(value, Entity) else None)
    if not isinstance(value, Entity):
        raise TypeError("Canvas requires an Entity or an extension that decomposes to Entities.")
    result = value.copy()
    result.set_style(value.effective_style)
    geometry = result.geometry
    if isinstance(geometry, Text):
        geometry.capture_layout()
        fonts = tuple(dict.fromkeys(run.font for run in geometry.layout.runs))
        if fonts:
            geometry.font = FontStack(fonts)
    elif isinstance(geometry, TeX):
        geometry.capture_layout()
    return result


def walk(drawings: Iterable[Entity]) -> Iterator[Entity]:
    for drawing in drawings:
        if isinstance(drawing, Group):
            yield from walk(drawing.members)
        else:
            yield drawing
