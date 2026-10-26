"""Reusable composites, explicit placement and ordered scene traversal."""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from pdl.geometry.bounds import Anchor, Bounds, geometry_bounds
from pdl.geometry.primitives import Geometry, Point
from pdl.geometry.transforms import Transform, transform_path
from pdl.scene.paint import Style
from pdl.typography.plain import Text
from pdl.typography.tex import TeX


@runtime_checkable
class Composite(Protocol):
    """An authoring object that decomposes to styled child drawings."""

    def decompose(self) -> tuple[Drawing, ...]: ...


type Graphic = Geometry | Composite


@dataclass(frozen=True)
class Drawing:
    """A graphic with optional explicit paint and a local transform."""

    geometry: Graphic
    style: Style | None = None
    transform: Transform = Transform()


@dataclass(frozen=True)
class Group:
    """An immutable reusable ordered composite with local coordinates.

    Child styles override inherited styles as a whole. Reusing a group does
    not mutate it; mutable child paths remain shared until explicitly copied.
    """

    children: tuple[Drawing, ...]
    transform: Transform = Transform()

    def decompose(self) -> tuple[Drawing, ...]:
        return tuple(
            Drawing(child.geometry, child.style, self.transform @ child.transform)
            for child in self.children
        )

    def transformed(self, transform: Transform) -> Group:
        return Group(self.children, transform @ self.transform)

    @property
    def bounds(self) -> Bounds:
        return bounds(self)

    def anchor(self, name: Anchor = "center") -> Point:
        return self.bounds.anchor(name)


def walk(
    drawings: tuple[Drawing, ...],
    transform: Transform = Transform(),
    style: Style | None = None,
    ancestors: frozenset[int] = frozenset(),
) -> Iterator[Drawing]:
    """Traverse composites without discarding leaf object identity."""
    for drawing in drawings:
        placement = transform @ drawing.transform
        paint = drawing.style if drawing.style is not None else style
        geometry = drawing.geometry
        if isinstance(geometry, Composite):
            if id(geometry) in ancestors:
                raise ValueError("Cyclic composite graph.")
            yield from walk(geometry.decompose(), placement, paint, ancestors | {id(geometry)})
        else:
            yield Drawing(geometry, paint, placement)


def bounds(graphic: Graphic) -> Bounds:
    """Return axis-aligned geometry/layout bounds, excluding stroke."""
    result: Bounds | None = None
    for drawing in walk((Drawing(graphic),)):
        geometry = drawing.geometry
        if isinstance(geometry, Composite):
            raise TypeError("Traversal must produce geometry leaves.")
        box = (
            geometry.layout_bounds.transformed(drawing.transform)
            if isinstance(geometry, (Text, TeX))
            else geometry_bounds(transform_path(geometry, drawing.transform))
        )
        result = box if result is None else result.union(box)
    return result if result is not None else Bounds(0, 0, 0, 0)
