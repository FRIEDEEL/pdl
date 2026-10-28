"""Numerical position inputs and internal immediate anchor queries."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from pdl.author.spaces import SpacePoint
from pdl.foundation.geometry.bounds import Anchor, Bounds
from pdl.foundation.geometry.primitives import Position

if TYPE_CHECKING:
    from pdl.author.composition import Drawing, Graphic


@dataclass(frozen=True)
class AnchorQuery:
    """A temporary request used only during one immediate measurement."""

    target: Graphic | Drawing
    name: Anchor = "center"

    def __post_init__(self) -> None:
        Bounds(0, 0, 0, 0).anchor(self.name)


type PointSource = Position | SpacePoint
