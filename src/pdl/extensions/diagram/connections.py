"""Numerically fixed polyline connections and filled triangular arrowheads."""

from __future__ import annotations

from math import hypot, isfinite

from pdl.author.entity.base import Entity
from pdl.author.entity.factories import Polygon, Polyline
from pdl.author.entity.group import Group
from pdl.author.geometry.frame import SpacePoint
from pdl.author.geometry.point import Point, Position, as_point
from pdl.author.style import Style


class Connection(Group):
    """An explicit route; references are resolved once at construction.

    The route has no automatic routing or live endpoint bindings. Duplicate
    consecutive positions are removed. Arrow lengths are clamped to one third
    of their adjacent segment. All members can be transformed as a Group.
    """

    def __init__(
        self,
        start: Position | SpacePoint,
        end: Position | SpacePoint,
        *,
        via: tuple[Position | SpacePoint, ...] = (),
        arrow_start: bool = False,
        arrow_end: bool = True,
        arrow_size: float = 2,
        style: Style = Style(line_width=0.4),
    ) -> None:
        if not isfinite(arrow_size) or arrow_size <= 0:
            raise ValueError("Arrow size must be positive and finite.")
        points: list[Point] = []
        for source in (start, *via, end):
            point = source.resolve() if isinstance(source, SpacePoint) else as_point(source)
            if not points or point != points[-1]:
                points.append(point)
        if len(points) < 2:
            raise ValueError("A connection needs at least two distinct consecutive points.")
        self._route = tuple(Entity(p) for p in points)
        self.arrow_start, self.arrow_end, self.arrow_size = arrow_start, arrow_end, arrow_size
        heads: list[Entity] = []
        for index, neighbor, enabled in ((0, 1, arrow_start), (-1, -2, arrow_end)):
            if not enabled or style.stroke is None or style.line_width == 0:
                continue
            tip, other = points[index], points[neighbor]
            length = hypot(tip.x - other.x, tip.y - other.y)
            size = min(arrow_size, length / 3)
            ux, uy = (tip.x - other.x) / length, (tip.y - other.y) / length
            base = Point(tip.x - size * ux, tip.y - size * uy)
            heads.append(
                Polygon(
                    (
                        tip,
                        (base.x - size * 0.4 * uy, base.y + size * 0.4 * ux),
                        (base.x + size * 0.4 * uy, base.y - size * 0.4 * ux),
                    ),
                    style=Style(stroke=None, fill=style.stroke),
                )
            )
            points[index] = base
        super().__init__(
            Polyline(tuple(points)), *heads, style=style, reference=self._point(self._route[0])
        )

    @staticmethod
    def _point(entity: Entity) -> Point:
        assert isinstance(entity.geometry, Point)
        return entity.geometry

    @property
    def start(self) -> Point:
        return self._point(self._route[0])

    @property
    def end(self) -> Point:
        return self._point(self._route[-1])

    @property
    def via(self) -> tuple[Point, ...]:
        return tuple(self._point(p) for p in self._route[1:-1])

    def _points(self) -> list[Point]:
        return [self._point(p) for p in self._route]

    def decompose(self) -> tuple[Entity, ...]:
        return tuple(member.copy().set_style(member.effective_style) for member in self.members)

    def _transform_entities(self) -> tuple[Entity, ...]:
        return (*super()._transform_entities(), *self._route)
