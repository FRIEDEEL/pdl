"""Geometric bounds and explicitly defined rectangular anchors."""

from __future__ import annotations

from dataclasses import dataclass
from math import sqrt
from typing import Literal

from pdl.geometry.primitives import Close, Cubic, Geometry, Move, Point, Quadratic, Segment
from pdl.geometry.transforms import Transform

type Anchor = Literal[
    "center",
    "north",
    "south",
    "east",
    "west",
    "north east",
    "north west",
    "south east",
    "south west",
]


@dataclass(frozen=True)
class Bounds:
    """An axis-aligned box excluding stroke and other paint effects."""

    left: float
    bottom: float
    right: float
    top: float

    @property
    def width(self) -> float:
        return self.right - self.left

    @property
    def height(self) -> float:
        return self.top - self.bottom

    def union(self, other: Bounds) -> Bounds:
        return Bounds(
            min(self.left, other.left),
            min(self.bottom, other.bottom),
            max(self.right, other.right),
            max(self.top, other.top),
        )

    def expanded(self, amount: float) -> Bounds:
        return Bounds(
            self.left - amount, self.bottom - amount, self.right + amount, self.top + amount
        )

    def transformed(self, transform: Transform) -> Bounds:
        points = [
            transform.apply(p)
            for p in (
                (self.left, self.bottom),
                (self.right, self.bottom),
                (self.right, self.top),
                (self.left, self.top),
            )
        ]
        return from_points(points)

    def anchor(self, name: Anchor = "center") -> Point:
        if name not in (
            "center",
            "north",
            "south",
            "east",
            "west",
            "north east",
            "north west",
            "south east",
            "south west",
        ):
            raise ValueError(f"Unknown anchor: {name}")
        return Point(
            self.left
            if "west" in name
            else self.right
            if "east" in name
            else (self.left + self.right) / 2,
            self.top
            if "north" in name
            else self.bottom
            if "south" in name
            else (self.top + self.bottom) / 2,
        )


def from_points(points: list[Point]) -> Bounds:
    if not points:
        return Bounds(0, 0, 0, 0)
    return Bounds(
        min(p.x for p in points),
        min(p.y for p in points),
        max(p.x for p in points),
        max(p.y for p in points),
    )


def _roots(a: float, b: float, c: float) -> list[float]:
    if abs(a) < 1e-14:
        return [-c / b] if abs(b) > 1e-14 else []
    discriminant = b * b - 4 * a * c
    if discriminant < 0:
        return []
    root = sqrt(discriminant)
    return [(-b + root) / (2 * a), (-b - root) / (2 * a)]


def geometry_bounds(geometry: Geometry) -> Bounds:
    """Compute exact bounds of line and quadratic/cubic path segments.

    Arc lowering follows the documented cubic approximation from Stage 1.
    Move-only paths use their move positions; empty paths use the origin.
    """
    points: list[Point] = []
    current = start = Point(0, 0)
    for command in geometry.to_path().commands:
        match command:
            case Move(end):
                start = current = end
                points.append(end)
            case Segment(end):
                points.append(end)
                current = end
            case Quadratic(control, end):
                for p0, p1, p2 in ((current.x, control.x, end.x), (current.y, control.y, end.y)):
                    denominator = p0 - 2 * p1 + p2
                    if denominator:
                        t = (p0 - p1) / denominator
                        if 0 < t < 1:
                            u = 1 - t
                            points.append(
                                Point(
                                    u * u * current.x + 2 * u * t * control.x + t * t * end.x,
                                    u * u * current.y + 2 * u * t * control.y + t * t * end.y,
                                )
                            )
                points.append(end)
                current = end
            case Cubic(c1, c2, end):
                for p0, p1, p2, p3 in (
                    (current.x, c1.x, c2.x, end.x),
                    (current.y, c1.y, c2.y, end.y),
                ):
                    for t in _roots(-p0 + 3 * p1 - 3 * p2 + p3, 2 * (p0 - 2 * p1 + p2), p1 - p0):
                        if 0 < t < 1:
                            u = 1 - t
                            points.append(
                                Point(
                                    u**3 * current.x
                                    + 3 * u * u * t * c1.x
                                    + 3 * u * t * t * c2.x
                                    + t**3 * end.x,
                                    u**3 * current.y
                                    + 3 * u * u * t * c1.y
                                    + 3 * u * t * t * c2.y
                                    + t**3 * end.y,
                                )
                            )
                points.append(end)
                current = end
            case Close():
                current = start
    return from_points(points)
