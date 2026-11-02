"""Minimal numerical contract for general two-dimensional transformations."""

from abc import ABC, abstractmethod
from typing import Protocol, Self


class TransformTarget(Protocol):
    """An editable target that delegates conversion to the transform package."""

    def apply_transform(self, transform: "Transform") -> Self: ...


class Transform(ABC):
    """Describe a spatial mapping without owning a geometry or drawing object.

    Concrete transformations map numerical coordinate pairs. Immediate Entity
    application delegates shape conversion and paint policy to this package's
    operations module. A transformation need not be affine, invertible, or
    expressible as a matrix; unsupported curve mappings are rejected explicitly.
    """

    @abstractmethod
    def apply(self, position: tuple[float, float]) -> tuple[float, float]:
        """Map a finite coordinate pair and return a new finite coordinate pair.

        Args:
            position: Numerical x/y coordinates; lengths are in millimeters.

        Returns:
            The mapped x/y coordinates in the same unit system.

        Raises:
            ValueError: Coordinates are nonfinite or outside the mapping's domain,
                or the result cannot be represented as finite coordinates.
        """
        raise NotImplementedError

    def apply_to[T: TransformTarget](self, target: T) -> T:
        """Apply immediately to a target and return that same target."""
        target.apply_transform(self)
        return target
