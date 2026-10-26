"""Explicit, non-routing connectors and vector arrowheads."""

from dataclasses import dataclass
from math import hypot, isfinite

from pdl.geometry.primitives import Point, Polygon, Polyline, point
from pdl.scene.composition import Drawing
from pdl.scene.evaluation import layout_session
from pdl.scene.paint import Style
from pdl.scene.references import AnchorRef, PointSource


@dataclass(frozen=True)
class Connection:
    """An explicitly routed polyline with optional filled triangle arrowheads.

    Coordinates and object anchors can be mixed. Anchor coordinates are
    evaluated at export time; fixed via points do not imply automatic routing.
    """

    start: PointSource
    end: PointSource
    via: tuple[PointSource, ...] = ()
    arrow_start: bool = False
    arrow_end: bool = True
    arrow_size: float = 2
    style: Style = Style(line_width=0.4)

    def __post_init__(self) -> None:
        if not isfinite(self.arrow_size) or self.arrow_size <= 0:
            raise ValueError("Arrow size must be positive and finite.")
        sources = (self.start, *self.via, self.end)
        for source in sources:
            if not isinstance(source, AnchorRef):
                point(source)
        if not any(isinstance(source, AnchorRef) for source in sources):
            self._points()

    def _points(self) -> list[Point]:
        with layout_session() as context:
            result: list[Point] = []
            for position in (self.start, *self.via, self.end):
                p = context.point(position)
                if not result or p != result[-1]:
                    result.append(p)
            if len(result) < 2:
                raise ValueError("A connection needs at least two distinct consecutive points.")
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
