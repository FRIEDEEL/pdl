"""Right-handed Cartesian coordinates and immutable affine frames."""

from __future__ import annotations

from dataclasses import dataclass
from math import cos, hypot, isfinite, radians, sin


@dataclass(frozen=True)
class Vector3D:
    """A finite displacement; angles use degrees and the right-hand rule."""

    x: float
    y: float
    z: float

    def __post_init__(self) -> None:
        if not all(isfinite(v) for v in (self.x, self.y, self.z)):
            raise ValueError("Components must be finite.")

    def dot(self, other: Vector3D) -> float:
        return self.x * other.x + self.y * other.y + self.z * other.z

    def cross(self, other: Vector3D) -> Vector3D:
        return Vector3D(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x,
        )

    def __mul__(self, factor: float) -> Vector3D:
        return Vector3D(self.x * factor, self.y * factor, self.z * factor)

    def __add__(self, other: Vector3D) -> Vector3D:
        return Vector3D(self.x + other.x, self.y + other.y, self.z + other.z)

    @property
    def length(self) -> float:
        return hypot(self.x, self.y, self.z)

    def normalized(self) -> Vector3D:
        if self.length == 0:
            raise ValueError("A zero vector has no direction.")
        return self * (1 / self.length)


@dataclass(frozen=True)
class Point3D:
    """A finite Cartesian position in millimeters."""

    x: float
    y: float
    z: float

    def __post_init__(self) -> None:
        Vector3D(self.x, self.y, self.z)

    def __sub__(self, other: Point3D) -> Vector3D:
        return Vector3D(self.x - other.x, self.y - other.y, self.z - other.z)

    def __add__(self, offset: Vector3D) -> Point3D:
        return Point3D(self.x + offset.x, self.y + offset.y, self.z + offset.z)


@dataclass(frozen=True)
class Transform3D:
    """Affine transform stored as basis columns and translation.

    ``a @ b`` applies b first. Scaling factors are dimensionless; translation
    uses millimeters. Singular transforms support forward mapping only.
    """

    x: Vector3D = Vector3D(1, 0, 0)
    y: Vector3D = Vector3D(0, 1, 0)
    z: Vector3D = Vector3D(0, 0, 1)
    offset: Vector3D = Vector3D(0, 0, 0)

    def apply_vector(self, v: Vector3D) -> Vector3D:
        return self.x * v.x + self.y * v.y + self.z * v.z

    def apply(self, p: Point3D) -> Point3D:
        v = self.apply_vector(Vector3D(p.x, p.y, p.z)) + self.offset
        return Point3D(v.x, v.y, v.z)

    def __matmul__(self, other: Transform3D) -> Transform3D:
        return Transform3D(
            self.apply_vector(other.x),
            self.apply_vector(other.y),
            self.apply_vector(other.z),
            self.apply_vector(other.offset) + self.offset,
        )

    def inverse(self) -> Transform3D:
        det = self.x.dot(self.y.cross(self.z))
        if det == 0:
            raise ValueError("Cannot invert a singular transform.")
        a, b, c = (
            v * (1 / det)
            for v in (self.y.cross(self.z), self.z.cross(self.x), self.x.cross(self.y))
        )
        linear = Transform3D(
            Vector3D(a.x, b.x, c.x), Vector3D(a.y, b.y, c.y), Vector3D(a.z, b.z, c.z)
        )
        return Transform3D(linear.x, linear.y, linear.z, linear.apply_vector(self.offset) * -1)

    @classmethod
    def translate(cls, x: float, y: float, z: float) -> Transform3D:
        return cls(offset=Vector3D(x, y, z))

    @classmethod
    def scale(cls, x: float, y: float | None = None, z: float | None = None) -> Transform3D:
        """Scale along each axis; omitted factors equal x."""
        return cls(
            Vector3D(x, 0, 0),
            Vector3D(0, x if y is None else y, 0),
            Vector3D(0, 0, x if z is None else z),
        )

    @classmethod
    def rotate(cls, angle: float, axis: Vector3D = Vector3D(0, 0, 1)) -> Transform3D:
        """Rotate about an arbitrary axis through the origin, in degrees."""
        if not isfinite(angle):
            raise ValueError("Angle must be finite.")
        a = axis.normalized()
        c, s = cos(radians(angle)), sin(radians(angle))

        def turn(v: Vector3D) -> Vector3D:
            return v * c + a.cross(v) * s + a * (a.dot(v) * (1 - c))

        return cls(turn(Vector3D(1, 0, 0)), turn(Vector3D(0, 1, 0)), turn(Vector3D(0, 0, 1)))


@dataclass(frozen=True)
class CoordinateSystem3D:
    """Immutable local-to-parent frame, independent of 2D Canvas mappings."""

    transform: Transform3D = Transform3D()
    parent: CoordinateSystem3D | None = None

    def child(self, transform: Transform3D = Transform3D()) -> CoordinateSystem3D:
        return CoordinateSystem3D(transform, self)

    def to_world(self) -> Transform3D:
        return self.transform if self.parent is None else self.parent.to_world() @ self.transform

    def convert_point(self, point: Point3D, target: CoordinateSystem3D) -> Point3D:
        """Convert local coordinates into target coordinates, in millimeters."""
        return (target.to_world().inverse() @ self.to_world()).apply(point)

    def convert_vector(self, vector: Vector3D, target: CoordinateSystem3D) -> Vector3D:
        """Convert a displacement, ignoring translations."""
        return (target.to_world().inverse() @ self.to_world()).apply_vector(vector)
