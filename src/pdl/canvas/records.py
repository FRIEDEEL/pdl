"""Narrow backend input contract, containing ordinary Author entities."""

from dataclasses import dataclass
from typing import Protocol

from pdl.author.entity.base import Entity
from pdl.author.transform.affine import AffineTransform


class Page(Protocol):
    @property
    def width(self) -> float: ...
    @property
    def height(self) -> float: ...
    @property
    def drawings(self) -> tuple[Entity, ...]: ...


@dataclass(frozen=True)
class Viewport:
    width: float
    height: float
    drawings: tuple[Entity, ...]
    output_transform: AffineTransform = AffineTransform()
