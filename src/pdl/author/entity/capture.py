"""State capture into the same Author Entity model used for editing."""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from typing import Protocol, runtime_checkable

from pdl.author.entity.base import Entity
from pdl.author.entity.group import Group
from pdl.author.geometry.tex import TeX
from pdl.author.geometry.text import Text
from pdl.author.style.font import FontStack
from pdl.author.style.style import Style


@runtime_checkable
class Composite(Protocol):
    """Extension hook: expand into core Author entities before rendering."""

    def decompose(self) -> tuple[Entity, ...]: ...


def freeze(value: Entity | Composite) -> Entity:
    """Capture state, effective styles, and typography without a second model."""
    return _freeze(value, frozenset(), root=True)


def _freeze(value: object, ancestors: frozenset[int], *, root: bool = False) -> Entity:
    if id(value) in ancestors:
        raise ValueError("Cyclic composite graph during capture.")
    ancestors = ancestors | {id(value)}
    if isinstance(value, Group):
        result = Group(
            *(_freeze(m, ancestors) for m in value.members),
            style=_capture_group_style(value, root=root),
            reference=value.reference,
            default_style=value.default_paint,
        )
        return result
    if isinstance(value, Composite):
        children = tuple(_freeze(m, ancestors) for m in value.decompose())
        return Group(
            *children,
            style=_capture_group_style(value, root=root) if isinstance(value, Entity) else None,
            default_style=value.default_paint if isinstance(value, Entity) else Group.default_style,
        )
    if not isinstance(value, Entity):
        raise TypeError("Canvas requires an Entity or an extension that decomposes to Entities.")
    result = value.copy(default_style=value.effective_style if root else value.default_paint)
    geometry = result.geometry
    if isinstance(geometry, Text):
        geometry.font = FontStack(geometry.resolved_fonts())
        geometry.capture_layout()
    elif isinstance(geometry, TeX):
        geometry.capture_layout()
    return result


def walk(drawings: Iterable[Entity]) -> Iterator[Entity]:
    for drawing in drawings:
        if isinstance(drawing, Group):
            yield from walk(drawing.members)
        else:
            yield drawing


def _capture_group_style(value: Entity, *, root: bool) -> Style | None:
    """Preserve explicit/None members; capture an omitted external parent context."""
    if value.style is not None or not root:
        return value.style
    ancestor = value.parent
    while ancestor is not None:
        if ancestor.style is not None:
            return ancestor.style
        ancestor = ancestor.parent
    return None
