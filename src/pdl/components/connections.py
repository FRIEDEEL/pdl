"""Explicit, non-routing connectors and vector arrowheads."""

from dataclasses import dataclass
from math import hypot, isfinite

from pdl.geometry.primitives import Point, Polygon, Polyline, point
from pdl.scene.composition import Drawing
from pdl.scene.entity import Entity
from pdl.scene.evaluation import layout_session
from pdl.scene.paint import Style
from pdl.scene.references import AnchorRef, PointSource
from pdl.scene.spaces import SpacePoint


@dataclass(eq=False)
class Connection(Entity):
    """A manually routed polyline with optional filled triangular arrowheads.

    Args:
        start: First endpoint, as coordinates or an anchor/space reference.
        end: Final endpoint.
        via: Intermediate points in route order. No automatic routing is performed.
        arrow_start: Draw an arrowhead at the start; false by default.
        arrow_end: Draw an arrowhead at the end; true by default.
        arrow_size: Positive nominal arrow length in millimeters. Short segments
            limit it to one third of the adjacent segment's length.
        style: Line paint; arrowheads use its stroke color.

    References are evaluated when measured/rendered. Dependencies do not add
    their target objects to the canvas. Consecutive duplicate points are removed.

    Raises:
        ValueError: Arrow size is invalid or fewer than two distinct consecutive
            points remain when the route is evaluated.
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
            if not isinstance(source, (AnchorRef, SpacePoint)):
                point(source)
        if not any(isinstance(source, (AnchorRef, SpacePoint)) for source in sources):
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
