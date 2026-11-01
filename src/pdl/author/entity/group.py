"""World-coordinate ownership groups with dynamic style fallback."""

from __future__ import annotations

from typing import Self

from pdl.author.entity.base import Entity
from pdl.author.geometry.bounds import Bounds
from pdl.author.geometry.point import Point, Position
from pdl.author.style.style import Style


class Group(Entity):
    """An ordered Entity owning members in world coordinates.

    Each member has at most one parent. Adding/removing never writes inherited
    paint into a member. Nested fallback uses the closest explicitly styled
    ancestor, then the member's own type default. Group edits affect existing
    members; later additions are not affected by past transformations.
    """

    def __init__(
        self, *members: Entity, style: Style | None = None, reference: Position = (0, 0)
    ) -> None:
        super().__init__(Point(0, 0), style=style, reference=reference)
        self._members: list[Entity] = []
        self.add(*members)

    @property
    def members(self) -> tuple[Entity, ...]:
        return tuple(self._members)

    def add(self, *members: Entity) -> Self:
        # Validate the entire batch before changing any ownership.
        for member in members:
            ancestor: Entity | None = self
            while ancestor is not None:
                if member is ancestor:
                    raise ValueError("Group ownership cannot contain cycles.")
                ancestor = ancestor.parent
            if member.parent is not None and member.parent is not self:
                raise ValueError("Remove the member from its existing Group first.")
        for member in members:
            if member not in self._members:
                self._members.append(member)
                member._parent = self
        return self

    def remove(self, *members: Entity) -> Self:
        for member in members:
            if member not in self._members:
                raise ValueError("Entity is not a member of this Group.")
        for member in dict.fromkeys(members):
            self._members.remove(member)
            member._parent = None
        return self

    def dismiss(self) -> tuple[Entity, ...]:
        members = self.members
        self.remove(*members)
        return members

    @property
    def bounds(self) -> Bounds:
        box = Bounds.empty()
        for member in self.members:
            box = box.union(member.bounds)
        return box

    @property
    def ink_bounds(self) -> Bounds:
        box = Bounds.empty()
        for member in self.members:
            box = box.union(member.ink_bounds)
        return box

    def _transform_entities(self) -> tuple[Entity, ...]:
        return (
            self,
            *(target for member in self.members for target in member._transform_entities()),
        )
