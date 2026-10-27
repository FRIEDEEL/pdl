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
    """An object with optional instance paint and local affine placement.

    Args:
        geometry: Shape, text, or composite definition to place.
        style: Whole-style override; ``None`` allows inherited or object defaults.
        transform: Local-to-parent matrix, identity by default.

    This frozen record does not freeze arbitrary user-owned mutable objects.
    Canvas.draw captures built-in mutable descriptions when recording it.
    """

    geometry: Graphic
    style: Style | None = None
    transform: Transform = Transform()

    def anchor(self, name: Anchor = "center") -> AnchorRef:
        """Reference this instance, including its explicit placement."""
        return AnchorRef(self, name)

    def transformed(self, transform: Transform) -> Drawing:
        """Return a new Drawing with the matrix applied outside its current placement."""
        return Drawing(self.geometry, self.style, transform @ self.transform)

    def child(self, index: int) -> Drawing:
        """Address a Group child with this instance's accumulated placement."""
        if not isinstance(self.geometry, Group):
            raise TypeError("Only an explicitly defined Group has addressable children.")
        child = self.geometry.child(index).transformed(self.transform)
        return Drawing(
            child.geometry,
            child.style if child.style is not None else self.style,
            child.transform,
        )


@dataclass(frozen=True)
class Group:
    """An ordered reusable assembly of Drawing records.

    Args:
        children: Drawings in paint order, expressed in group-local coordinates.
        transform: Group-local to parent matrix, identity by default.

    The Group record is immutable, but child paths can remain mutable until
    captured by Canvas.draw. Explicit child styles override inherited styles
    as a whole. Group transforms move members together without recomputing spacing.
    Its anchor refers to axis-aligned group bounds; use child anchors for ports.
    """

    children: tuple[Drawing, ...]
    transform: Transform = Transform()

    def decompose(self) -> tuple[Drawing, ...]:
        return tuple(
            Drawing(child.geometry, child.style, self.transform @ child.transform)
            for child in self.children
        )

    def transformed(self, transform: Transform) -> Group:
        """Return a new Group with an outer matrix, leaving this definition unchanged."""
        return Group(self.children, transform @ self.transform)

    def child(self, index: int) -> Drawing:
        """Address a child in this group's parent coordinate space."""
        return self.children[index].transformed(self.transform)

    @property
    def bounds(self) -> Bounds:
        """Measure authoring layout bounds under the current typography context.

        For canvas-configured measurements, prefer ``canvas.query().bounds(...)``.
        """
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
    """Measure authoring axis-aligned geometry/layout bounds without stroke.

    Args:
        graphic: Shape, text, composite, or placed Drawing.

    Returns:
        Bounds before Canvas viewport adaptation. Typography uses the current
        context; prefer ``canvas.query().bounds`` when canvas fonts/mappings matter.
    """
    with layout_session() as context:
        return context.bounds(graphic)
