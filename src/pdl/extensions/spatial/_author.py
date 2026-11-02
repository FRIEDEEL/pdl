"""Small construction helpers producing ordinary Author Entities."""

from pdl.author.entity.base import Entity
from pdl.author.entity.factories import as_entity as make_entity
from pdl.author.entity.group import Group


def make_group(children: tuple[Entity, ...]) -> Group:
    return Group(*children)


__all__ = ["make_entity", "make_group"]
