"""Explicit frame visualization with current numerical basis data."""

from math import isfinite

from pdl.author.entity.base import Entity
from pdl.author.entity.group import Group
from pdl.author.geometry.frame import Frame
from pdl.author.geometry.point import Point, Position, Vector, as_point
from pdl.author.geometry.shapes import Circle, Line
from pdl.author.style import BLACK, Color, Style


class FrameAxes(Group):
    """A drawable frame explicitly created from a pure geometric Frame.

    The current Frame is the Group's geometry. Its visual members and basis
    transform immediately together. Ordinary Entities never acquire a Frame.
    """

    def __init__(
        self,
        frame: Frame,
        *,
        length: float = 10,
        origin_radius: float = 0.5,
        style: Style | None = None,
        x_style: Style | None = None,
        y_style: Style | None = None,
        origin_style: Style | None = None,
    ) -> None:
        if not all(isfinite(v) and v > 0 for v in (length, origin_radius)):
            raise ValueError("Frame display lengths must be positive and finite.")
        p = as_point(frame.origin)
        x = Entity(
            Line(p, frame.point((length, 0))),
            style=x_style or style or Style(stroke=Color(0.8, 0.2, 0.2), line_width=0.35),
        )
        y = Entity(
            Line(p, frame.point((0, length))),
            style=y_style or style or Style(stroke=Color(0.2, 0.3, 0.8), line_width=0.35),
        )
        marker = Entity(
            Circle(p, origin_radius), style=origin_style or Style(stroke=None, fill=BLACK)
        )
        super().__init__(x, y, marker, style=style, reference=p)
        self._geometry = frame

    @property
    def geometry(self) -> Frame:
        value = super().geometry
        assert isinstance(value, Frame)
        return value

    @property
    def frame(self) -> Frame:
        return self.geometry

    @property
    def origin(self) -> Point:
        return as_point(self.frame.origin)

    def point(self, position: Position) -> Point:
        return self.frame.point(position)

    def vector(self, vector: Position | Vector) -> Vector:
        return self.frame.vector(vector)
