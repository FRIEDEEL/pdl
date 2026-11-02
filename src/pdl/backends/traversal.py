"""Traversal of ordinary captured Author objects; no resolved scene hierarchy."""

from collections.abc import Iterable, Iterator

from pdl.author.entity.base import Entity
from pdl.author.entity.group import Group


def walk(drawings: Iterable[Entity]) -> Iterator[Entity]:
    for drawing in drawings:
        if isinstance(drawing, Group):
            yield from walk(drawing.members)
        else:
            yield drawing
