"""Minimal numerical contract for general two-dimensional transformations."""

from abc import ABC, abstractmethod


class Transform(ABC):
    """Describe a spatial mapping without owning a geometry or drawing object.

    Concrete transformations map numerical coordinate pairs. Geometry and
    Entity types decide how to use a mapping, whether they support it, and
    whether to modify themselves or return new objects. A transformation need
    not be affine, invertible, or expressible as a matrix.
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
