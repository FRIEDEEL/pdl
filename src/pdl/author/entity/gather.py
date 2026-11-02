"""Explicit selections without ownership or inherited paint."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Self

from pdl.author.entity.base import Entity, TransformEdit
from pdl.author.geometry.bounds import Bounds
from pdl.author.geometry.point import Position
from pdl.author.style.style import Style
from pdl.author.transform.affine import Reflection, Rotation, Scaling
from pdl.author.transform.affine import Translation as _translation
from pdl.author.transform.base import Transform


class Gather:
    """An ordered identity-deduplicated selection of Entity objects.

    Style updates affect exactly selected objects; selecting a Group does not
    expand its members. Transforming a selected Group naturally transforms its
    members, and overlapping selections are transformed once.
    """

    def __init__(self, *members: Entity) -> None:
        self._members: list[Entity] = []
        self.add(*members)

    @property
    def members(self) -> tuple[Entity, ...]:
        return tuple(self._members)

    def __iter__(self) -> Iterator[Entity]:
        return iter(self.members)

    def __len__(self) -> int:
        return len(self._members)

    def add(self, *members: Entity) -> Self:
        for member in members:
            if member not in self._members:
                self._members.append(member)
        return self

    def remove(self, *members: Entity) -> Self:
        for member in members:
            if member in self._members:
                self._members.remove(member)
        return self

    def set_style(self, style: Style | None) -> Self:
        for member in self.members:
            member.set_style(style)
        return self

    def set_opacity(self, opacity: float) -> Self:
        for member in self.members:
            member.set_opacity(opacity)
        return self

    @property
    def bounds(self) -> Bounds:
        box = Bounds.empty()
        for member in self.members:
            box = box.union(member.bounds)
        return box

    def apply_transform(self, transform: Transform) -> Self:
        selected = set(self.members)
        roots: list[Entity] = []
        for member in self.members:
            ancestor = member.parent
            while ancestor is not None and ancestor not in selected:
                ancestor = ancestor.parent
            if ancestor is None:
                roots.append(member)
        plans: list[TransformEdit] = []
        for member in roots:
            plans.extend(member.prepare_transform(transform))
        Entity.commit_transform(plans)
        return self

    def translate(self, x: float, y: float) -> Self:
        return self.apply_transform(_translation(x, y))

    def rotate(self, angle: float, *, origin: Position | None = None) -> Self:
        pivot = self.bounds.anchor() if origin is None else origin
        return self.apply_transform(Rotation(angle).around(pivot))

    def scale(self, x: float, y: float | None = None, *, origin: Position | None = None) -> Self:
        pivot = self.bounds.anchor() if origin is None else origin
        return self.apply_transform(Scaling(x, y).around(pivot))

    def reflect(self, angle: float = 0, *, origin: Position | None = None) -> Self:
        pivot = self.bounds.anchor() if origin is None else origin
        return self.apply_transform(Reflection(angle).around(pivot))

    def union(self, other: Gather) -> Gather:
        return Gather(*self.members, *other.members)

    def intersection(self, other: Gather) -> Gather:
        return Gather(*(m for m in self.members if m in other.members))

    def difference(self, other: Gather) -> Gather:
        return Gather(*(m for m in self.members if m not in other.members))

    def __or__(self, other: Gather) -> Gather:
        return self.union(other)

    def __and__(self, other: Gather) -> Gather:
        return self.intersection(other)

    def __sub__(self, other: Gather) -> Gather:
        return self.difference(other)
