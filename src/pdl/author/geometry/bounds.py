"""Geometric bounds and explicitly defined rectangular anchors."""

from __future__ import annotations

from dataclasses import dataclass
from math import atan2, cos, degrees, hypot, radians, sin, sqrt
from typing import Literal, Protocol, runtime_checkable

from pdl.author.geometry.path import (
    Close,
    Cubic,
    Move,
    Quadratic,
    Segment,
)
from pdl.author.geometry.point import Point, Position, as_point
from pdl.author.geometry.protocols import PathSource
from pdl.author.transform.affine import AffineTransform as Transform


@runtime_checkable
class CircleGeometry(Protocol):
    """Numerical circle parameters, independent of drawing objects."""

    center: Position
    radius: float


@runtime_checkable
class EllipticalArcGeometry(Protocol):
    """Numerical ellipse parameters for exact transformed extrema."""

    center: Position
    radius_x: float
    radius_y: float
    rotation: float
    start_angle: float
    sweep_angle: float


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
    is_empty: bool = False

    @classmethod
    def empty(cls) -> Bounds:
        """Represent absence of geometry, distinct from a point at the origin."""
        return cls(0, 0, 0, 0, is_empty=True)

    @property
    def width(self) -> float:
        return self.right - self.left

    @property
    def height(self) -> float:
        return self.top - self.bottom

    def union(self, other: Bounds) -> Bounds:
        if self.is_empty:
            return other
        if other.is_empty:
            return self
        return Bounds(
            min(self.left, other.left),
            min(self.bottom, other.bottom),
            max(self.right, other.right),
            max(self.top, other.top),
        )

    def expanded(self, amount: float) -> Bounds:
        if self.is_empty:
            return self
        return Bounds(
            self.left - amount, self.bottom - amount, self.right + amount, self.top + amount
        )

    def transformed(self, transform: Transform) -> Bounds:
        if self.is_empty:
            return self
        points = [
            Point(*transform.apply(p))
            for p in (
                (self.left, self.bottom),
                (self.right, self.bottom),
                (self.right, self.top),
                (self.left, self.top),
            )
        ]
        return from_points(points)

    def anchor(self, name: Anchor = "center") -> Point:
        if self.is_empty:
            raise ValueError("Empty geometry has no anchor.")
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
        return Bounds.empty()
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


def geometry_bounds(geometry: PathSource) -> Bounds:
    """Compute exact bounds of line and quadratic/cubic path segments.

    Arc lowering follows the documented cubic approximation from Stage 1.
    Move-only paths use their move positions; empty paths use the origin.
    """
    if isinstance(geometry, (CircleGeometry, EllipticalArcGeometry)):
        return transformed_bounds(geometry, Transform())
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


def transformed_bounds(geometry: PathSource, transform: Transform) -> Bounds:
    """Find tight affine bounds without approximating circular/elliptical geometry."""

    if isinstance(geometry, CircleGeometry):
        center = Point(*transform.apply((as_point(geometry.center).x, as_point(geometry.center).y)))
        dx = geometry.radius * hypot(transform.a, transform.c)
        dy = geometry.radius * hypot(transform.b, transform.d)
        return Bounds(center.x - dx, center.y - dy, center.x + dx, center.y + dy)
    if isinstance(geometry, EllipticalArcGeometry):
        angle = radians(geometry.rotation)
        ux, uy = geometry.radius_x * cos(angle), geometry.radius_x * sin(angle)
        vx, vy = -geometry.radius_y * sin(angle), geometry.radius_y * cos(angle)
        u = Point(transform.a * ux + transform.c * uy, transform.b * ux + transform.d * uy)
        v = Point(transform.a * vx + transform.c * vy, transform.b * vx + transform.d * vy)
        center = Point(*transform.apply((as_point(geometry.center).x, as_point(geometry.center).y)))
        start, sweep = geometry.start_angle, geometry.sweep_angle
        angles = [start, start + sweep]
        for x, y in ((u.x, v.x), (u.y, v.y)):
            extremum = degrees(atan2(y, x))
            for candidate in (extremum, extremum + 180):
                distance = (candidate - start) % 360 if sweep >= 0 else (start - candidate) % 360
                if distance <= abs(sweep):
                    angles.append(candidate)
        return from_points(
            [
                Point(
                    center.x + u.x * cos(radians(t)) + v.x * sin(radians(t)),
                    center.y + u.y * cos(radians(t)) + v.y * sin(radians(t)),
                )
                for t in angles
            ]
        )
    return geometry_bounds(geometry.to_path().mapped(transform))
