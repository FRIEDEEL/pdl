"""Explicit, non-routing connectors and vector arrowheads."""

from dataclasses import dataclass
from math import hypot, isfinite

from pdl.geometry.primitives import Point, Polygon, Polyline, Position, point
from pdl.scene.composition import Drawing
from pdl.scene.paint import Style


@dataclass(frozen=True)
class Connection:
    """An explicitly routed polyline with optional filled triangle arrowheads.

    Endpoints are snapshots, not live references. Define and position nodes
    first, then obtain anchors and construct their connections.
    """

    start: Position
    end: Position
    via: tuple[Position, ...] = ()
    arrow_start: bool = False
    arrow_end: bool = True
    arrow_size: float = 2
    style: Style = Style(line_width=0.4)

    def __post_init__(self) -> None:
        if not isfinite(self.arrow_size) or self.arrow_size <= 0:
            raise ValueError("Arrow size must be positive and finite.")
        if len(self._points()) < 2:
            raise ValueError("A connection needs at least two distinct consecutive points.")

    def _points(self) -> list[Point]:
        result: list[Point] = []
        for position in (self.start, *self.via, self.end):
            p = point(position)
            if not result or p != result[-1]:
                result.append(p)
        return result

    def decompose(self) -> tuple[Drawing, ...]:
        points = self._points()
        heads: list[Drawing] = []
        for index, neighbor, enabled in ((0, 1, self.arrow_start), (-1, -2, self.arrow_end)):
            if not enabled or self.style.stroke is None or self.style.line_width == 0:
                continue
            tip, other = points[index], points[neighbor]
            length = hypot(tip.x - other.x, tip.y - other.y)
            size = min(self.arrow_size, length / 3)
            ux, uy = (tip.x - other.x) / length, (tip.y - other.y) / length
            base = Point(tip.x - size * ux, tip.y - size * uy)
            triangle = Polygon(
                (
                    tip,
                    (base.x - size * 0.4 * uy, base.y + size * 0.4 * ux),
                    (base.x + size * 0.4 * uy, base.y - size * 0.4 * ux),
                )
            )
            heads.append(Drawing(triangle, Style(stroke=None, fill=self.style.stroke)))
            points[index] = base
        return (Drawing(Polyline(tuple(points)), self.style), *heads)
