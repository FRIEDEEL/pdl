"""Immutable affine matrices with concrete translation, rotation, and scale types."""

from __future__ import annotations

from dataclasses import dataclass
from math import cos, isfinite, radians, sin

from pdl.author.geometry.point import Point, Position, Vector, as_point
from pdl.author.transform.base import Transform


@dataclass(frozen=True, eq=False)
class AffineTransform(Transform):
    """A finite two-dimensional affine matrix, identity by default.

    The coefficients represent homogeneous rows ``(a, c, e)``, ``(b, d, f)``,
    and ``(0, 0, 1)``. Thus x' = a*x + c*y + e and y' = b*x + d*y + f.
    ``left @ right`` applies right first, then left. Composition returns a
    general AffineTransform, even when both operands have concrete subclasses.

    This value owns no geometry, Entity, Style, or reference point. Coordinates
    and translations are in millimeters; scale and shear are dimensionless.
    Singular matrices are valid mappings, but cannot be inverted. Matrix-value
    equality and hashing work across all affine subclasses.

    Args:
        a: X-to-x coefficient.
        b: X-to-y coefficient.
        c: Y-to-x coefficient.
        d: Y-to-y coefficient.
        e: Horizontal translation in millimeters.
        f: Vertical translation in millimeters.

    Raises:
        ValueError: A coefficient is infinite or NaN.
    """

    a: float = 1
    b: float = 0
    c: float = 0
    d: float = 1
    e: float = 0
    f: float = 0

    def __post_init__(self) -> None:
        if not all(isfinite(value) for value in self.values):
            raise ValueError("Affine matrix coefficients must be finite.")

    @property
    def values(self) -> tuple[float, float, float, float, float, float]:
        """Return coefficients in (a, b, c, d, e, f) order."""
        return self.a, self.b, self.c, self.d, self.e, self.f

    @property
    def matrix(self) -> tuple[tuple[float, float, float], ...]:
        """Return the three rows of the homogeneous 3-by-3 matrix."""
        return ((self.a, self.c, self.e), (self.b, self.d, self.f), (0, 0, 1))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, AffineTransform):
            return NotImplemented
        return self.values == other.values

    def __hash__(self) -> int:
        return hash(self.values)

    def apply(self, position: tuple[float, float]) -> tuple[float, float]:
        """Map a coordinate pair without changing the input or matrix.

        Raises:
            ValueError: Input or output coordinates are infinite or NaN.
        """
        x, y = position
        if not isfinite(x) or not isfinite(y):
            raise ValueError("Input coordinates must be finite.")
        result = (self.a * x + self.c * y + self.e, self.b * x + self.d * y + self.f)
        if not all(isfinite(value) for value in result):
            raise ValueError("Transformed coordinates must be finite.")
        return result

    def map(self, position: Position) -> Point:
        """Map a domain point without retaining it or any object state."""
        p = as_point(position)
        return Point(*self.apply((p.x, p.y)))

    def apply_vector(self, vector: Vector) -> Vector:
        """Map a displacement, omitting translation."""
        return Vector(self.a * vector.x + self.c * vector.y, self.b * vector.x + self.d * vector.y)

    @property
    def determinant(self) -> float:
        return self.a * self.d - self.b * self.c

    def __matmul__(self, other: object) -> AffineTransform:
        """Compose affine matrices; apply other first, then this matrix.

        General non-affine composition is not implemented by this operation.

        Raises:
            ValueError: Resulting coefficients overflow the finite representation.
        """
        if not isinstance(other, AffineTransform):
            return NotImplemented
        return AffineTransform(
            self.a * other.a + self.c * other.b,
            self.b * other.a + self.d * other.b,
            self.a * other.c + self.c * other.d,
            self.b * other.c + self.d * other.d,
            self.a * other.e + self.c * other.f + self.e,
            self.b * other.e + self.d * other.f + self.f,
        )

    def inverse(self) -> AffineTransform:
        """Return the inverse without imposing a determinant tolerance.

        Rows are normalized separately to avoid avoidable overflow or underflow
        for very large or small coordinate scales. Floating-point rounding still
        limits accuracy for ill-conditioned matrices.

        Raises:
            ValueError: The matrix is singular at working precision or its inverse
                cannot be represented with finite coefficients.
        """
        row_x, row_y = max(abs(self.a), abs(self.c)), max(abs(self.b), abs(self.d))
        if row_x == 0 or row_y == 0:
            raise ValueError("Cannot invert a singular affine transform.")
        a, c = self.a / row_x, self.c / row_x
        b, d = self.b / row_y, self.d / row_y
        determinant = a * d - b * c
        if determinant == 0:
            raise ValueError("Cannot invert a singular affine transform.")
        ia, ic = d / determinant / row_x, -c / determinant / row_y
        ib, id_ = -b / determinant / row_x, a / determinant / row_y
        return AffineTransform(
            ia, ib, ic, id_, -(ia * self.e + ic * self.f), -(ib * self.e + id_ * self.f)
        )

    def around(self, pivot: Position) -> AffineTransform:
        """Express this mapping relative to an explicitly supplied pivot.

        Returns T(pivot) @ self @ T(-pivot). For rotation and scaling the pivot
        stays fixed; translation is unaffected. No default object reference
        point is selected here.

        Args:
            pivot: Finite x/y coordinates in millimeters.

        Returns:
            A new affine matrix using the supplied pivot.
        """
        p = as_point(pivot)
        x, y = p.x, p.y
        return Translation(x, y) @ self @ Translation(-x, -y)


class Translation(AffineTransform):
    """Translate by x/y distances in millimeters."""

    def __init__(self, x: float, y: float) -> None:
        super().__init__(e=x, f=y)


class Rotation(AffineTransform):
    """Rotate counterclockwise by angle degrees about the coordinate origin.

    Use ``around((x, y))`` for an explicit pivot. Object-specific default
    reference points are chosen by the geometry or Entity, not this class.
    """

    def __init__(self, angle: float) -> None:
        if not isfinite(angle):
            raise ValueError("Rotation angle must be finite.")
        c, s = cos(radians(angle)), sin(radians(angle))
        super().__init__(a=c, b=s, c=-s, d=c)


class Scaling(AffineTransform):
    """Scale coordinate axes about the origin; omitted y uses uniform scaling.

    Zero and negative factors are permitted. A zero factor produces a singular
    mapping. This mathematical operation does not change any Style parameters.
    """

    def __init__(self, x: float, y: float | None = None) -> None:
        super().__init__(a=x, d=x if y is None else y)


class Shear(AffineTransform):
    """Apply x' = x + x_factor*y and y' = y + y_factor*x."""

    def __init__(self, x_factor: float = 0, y_factor: float = 0) -> None:
        super().__init__(b=y_factor, c=x_factor)


class Reflection(AffineTransform):
    """Reflect across a line through the origin at angle degrees from positive x.

    Angle zero reflects across the x axis. Use ``around((x, y))`` to place the
    reflection line through an explicit point instead of the origin.
    """

    def __init__(self, angle: float = 0) -> None:
        if not isfinite(angle):
            raise ValueError("Reflection angle must be finite.")
        c, s = cos(2 * radians(angle)), sin(2 * radians(angle))
        super().__init__(a=c, b=s, c=s, d=-c)


class Rescale(Scaling):
    """Uniform scaling, optionally including stroke width.

    Args:
        factor: Finite uniform factor, including zero or negative values.
        include_linewidth: Scale stroke width by abs(factor), default False.

    Nonuniform scaling uses Scaling and has no line-width option. This explicit
    operation may materialize an inherited style on its target when requested.
    Matrix composition produces a plain AffineTransform; apply this operation
    separately when its paint option is required.
    """

    def __init__(self, factor: float, *, include_linewidth: bool = False) -> None:
        super().__init__(factor)
        object.__setattr__(self, "include_linewidth", include_linewidth)
        object.__setattr__(self, "factor", factor)

    include_linewidth: bool
    factor: float

    def around(self, pivot: Position) -> Rescale:
        """Keep the uniform scale's paint option when choosing a pivot."""
        matrix = super().around(pivot)
        result = Rescale(self.factor, include_linewidth=self.include_linewidth)
        object.__setattr__(result, "e", matrix.e)
        object.__setattr__(result, "f", matrix.f)
        return result
