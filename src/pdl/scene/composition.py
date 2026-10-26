"""Reusable composites, explicit placement and ordered scene traversal."""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from pdl.geometry.bounds import Anchor, Bounds
from pdl.geometry.primitives import Geometry
from pdl.geometry.transforms import Transform
from pdl.scene.evaluation import layout_session
from pdl.scene.paint import Style
from pdl.scene.references import AnchorRef


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

    def anchor(self, name: Anchor = "center") -> AnchorRef:
        """Reference this instance, including its explicit placement."""
        return AnchorRef(self, name)

    def transformed(self, transform: Transform) -> Drawing:
        return Drawing(self.geometry, self.style, transform @ self.transform)


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

    def anchor(self, name: Anchor = "center") -> AnchorRef:
        """Reference the axis-aligned bounds of this placed group."""
        return AnchorRef(self, name)


def walk(
    drawings: tuple[Drawing, ...],
    transform: Transform = Transform(),
    style: Style | None = None,
    ancestors: frozenset[int] = frozenset(),
) -> Iterator[Drawing]:
    """Traverse composites without discarding leaf object identity."""
    with layout_session() as context:
        for drawing in drawings:
            placement = transform @ drawing.transform
            paint = drawing.style if drawing.style is not None else style
            geometry = drawing.geometry
            if isinstance(geometry, Composite):
                if id(geometry) in ancestors:
                    raise ValueError("Cyclic composite graph.")
                yield from walk(
                    context.decompose(geometry), placement, paint, ancestors | {id(geometry)}
                )
            else:
                yield Drawing(geometry, paint, placement)


def bounds(graphic: Graphic | Drawing) -> Bounds:
    """Return axis-aligned geometry/layout bounds, excluding stroke."""
    with layout_session() as context:
        return context.bounds(graphic)
