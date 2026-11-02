"""Small structural contracts, not a universal Geometry hierarchy."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from pdl.author.geometry.path import Path


@runtime_checkable
class PathSource(Protocol):
    """A shape with an explicit path conversion."""

    def to_path(self) -> Path: ...


class Mapping(Protocol):
    """A numerical mapping independent of shape or drawing types."""

    def apply(self, position: tuple[float, float]) -> tuple[float, float]: ...
