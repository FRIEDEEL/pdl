"""Read-only page contract consumed by output adapters.

Drawing records are ordinary Author descriptions captured on submission. This
contract adds page dimensions, not a second representation of drawing objects.
"""

from typing import Protocol

from pdl.author.composition import Drawing


class Page(Protocol):
    """A sized, ordered collection of captured draw records."""

    @property
    def width(self) -> float: ...
    @property
    def height(self) -> float: ...
    @property
    def drawings(self) -> tuple[Drawing, ...]: ...
