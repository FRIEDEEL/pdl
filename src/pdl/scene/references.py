"""Deferred positions expressed in the referencing object's coordinate space."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from pdl.geometry.bounds import Anchor, Bounds
from pdl.geometry.primitives import Position, point

if TYPE_CHECKING:
    from pdl.scene.composition import Drawing, Graphic


@dataclass(frozen=True)
class AnchorRef:
    """An object anchor, evaluated with the renderer's font and layout policy.

    Reference a placed Drawing or transformed Group to address an instance.
    References to children inside a shared group use that group's local
    coordinates; rendering the group applies its placement to both children
    and connections together.
    """

    target: Graphic | Drawing
    name: Anchor = "center"
    offset: Position = (0, 0)

    def __post_init__(self) -> None:
        Bounds(0, 0, 0, 0).anchor(self.name)
        point(self.offset)

    def __add__(self, offset: Position) -> AnchorRef:
        first, second = point(self.offset), point(offset)
        return AnchorRef(self.target, self.name, (first.x + second.x, first.y + second.y))


type PointSource = Position | AnchorRef
