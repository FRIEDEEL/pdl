"""Flat, overlapping operation sets that never reparent their members."""

from __future__ import annotations

from typing import Self
from warnings import warn

from pdl.author.composition import Group
from pdl.author.entity import Entity
from pdl.author.references import PointSource
from pdl.author.style import Style
from pdl.foundation.geometry.primitives import Position
from pdl.foundation.geometry.transforms import Transform

type Target = Entity | Group


class Gather:
    """A flat identity set of top-level instances for imperative operations.

    Args:
        members: Entity/Group targets or other Gathers. Gathers are immediately
            flattened; subsequent membership changes are independent.

    Grouped children promote to their outermost Group with a warning. Targets
    are normalized and deduplicated again before every operation, so regrouping
    after selection cannot cause double transformations. Gather is not drawable.
    """

    def __init__(self, *members: Target | Gather) -> None:
        self._members: dict[int, Target] = {}
        self.add(*members)

    @property
    def members(self) -> tuple[Target, ...]:
        """Return current unique outermost targets in selection order."""
        result: dict[int, Target] = {}
        for member in self._members.values():
            if isinstance(member, Group) and member.dismissed:
                raise ValueError("Gather targets a dismissed Group; create a new selection.")
            root = member.root
            if root is not member:
                warn("Gather target promoted to its outermost Group.", UserWarning, stacklevel=2)
            result[id(root)] = root
        return tuple(result.values())

    def add(self, *members: Target | Gather) -> Self:
        """Union in current members; nested Gathers never remain in the set."""
        for member in members:
            targets = member.members if isinstance(member, Gather) else (member,)
            for target in targets:
                root = target.root
                if root is not target:
                    warn(
                        "Gather target promoted to its outermost Group.", UserWarning, stacklevel=2
                    )
                self._members[id(root)] = root
        return self

    def remove(self, *members: Target | Gather) -> Self:
        """Remove normalized targets; missing targets are ignored."""
        removed = {id(m) for m in Gather(*members).members}
        self._members = {id(m): m for m in self.members if id(m) not in removed}
        return self

    def union(self, other: Gather) -> Gather:
        """Return a new membership snapshot containing either selection."""
        return Gather(self, other)

    def intersection(self, other: Gather) -> Gather:
        """Return current targets common to both selections."""
        identities = {id(m) for m in other.members}
        return Gather(*(m for m in self.members if id(m) in identities))

    def difference(self, other: Gather) -> Gather:
        """Return current targets absent from the other selection."""
        identities = {id(m) for m in other.members}
        return Gather(*(m for m in self.members if id(m) not in identities))

    def transform(self, transform: Transform) -> Self:
        """Apply one world-space matrix once per current operation unit."""
        from pdl.author.composition import Drawing
        from pdl.author.placement import Placement

        targets = self.members
        # Capture every starting state before editing any shared reference target.
        states = {id(member): member.snapshot() for member in targets}
        for member in targets:
            if not isinstance(member, Group):
                member.placement = Placement(Drawing(states[id(member)]))
            member.apply_transform(transform)
        return self

    def translate(self, x: float, y: float) -> Self:
        """Translate each target by world millimeters."""
        return self.transform(Transform.translate(x, y))

    def rotate(self, angle: float, *, about: PointSource | None = None) -> Self:
        """Rotate together around one world pivot, defaulting to the world origin."""
        return self.transform(Transform.rotate(angle).around(self._pivot(about)))

    def scale(
        self,
        x: float,
        y: float | None = None,
        *,
        about: PointSource | None = None,
    ) -> Self:
        """Scale together around one world pivot, defaulting to the world origin."""
        return self.transform(Transform.scale(x, y).around(self._pivot(about)))

    @staticmethod
    def _pivot(about: PointSource | None) -> Position:
        from pdl.author.measurement import layout_session

        with layout_session() as context:
            return context.point(about if about is not None else (0, 0))

    def reflect(self, angle: float = 0, *, origin: Position = (0, 0)) -> Self:
        """Reflect targets about one world line."""
        return self.transform(Transform.reflect(angle, origin))

    def set_style(self, style: Style) -> Self:
        """Assign a whole-style override to each target; no inherited Gather state."""
        from dataclasses import replace

        for member in self.members:
            if isinstance(member, Group):
                member.style = style
            else:
                member.placement = replace(
                    member.placement, drawing=replace(member.placement.drawing, style=style)
                )
        return self

    def set_opacity(self, opacity: float) -> Self:
        """Set per-target opacity, not an isolated composite-group opacity.

        Targets with no instance style receive the default Style. Existing
        explicit child styles continue to override Group inheritance.
        """
        from dataclasses import replace

        from pdl.author.placement import Placement
        from pdl.author.style import BLACK
        from pdl.author.tex import TeX
        from pdl.author.text import Text

        for member in self.members:
            style = member.style if isinstance(member, Group) else member.placement.paint
            default = Style()
            if not isinstance(member, Group):
                geometry = member.placement.drawing.geometry
                while isinstance(geometry, Placement):
                    geometry = geometry.drawing.geometry
                if isinstance(geometry, (Text, TeX)):
                    default = Style(stroke=None, fill=BLACK)
            self_style = replace(style or default, opacity=opacity)
            Gather(member).set_style(self_style)
        return self
