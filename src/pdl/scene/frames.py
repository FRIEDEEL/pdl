"""Non-painting reference frames and points with explicit visualization."""

from __future__ import annotations

from math import isfinite
from typing import TYPE_CHECKING, Self

from pdl.geometry.primitives import Line, Point, Position, Vector, point
from pdl.geometry.transforms import Transform
from pdl.scene.entity import Entity
from pdl.scene.spaces import CoordinateSystem, SpacePoint, SpaceVector

if TYPE_CHECKING:
    from pdl.geometry.bounds import Anchor
    from pdl.scene.composition import Drawing, Group
    from pdl.scene.paint import Style
    from pdl.scene.references import AnchorRef, PointSource


class Frame(Entity):
    """A non-painting affine reference defined by an origin and two basis vectors.

    Args:
        origin: Origin in authoring-world millimeters, default (0, 0).
        x_basis: Displacement for one local x unit, default (1, 0).
        y_basis: Displacement for one local y unit, default (0, 1).

    A local pair (u, v) means origin + u*x_basis + v*y_basis. Bases may be
    skewed, scaled or singular; only inverse conversions require invertibility.
    Frames produce no paint, visible bounds, or occlusion. Transform them
    explicitly or include them in a Gather/Group to follow other objects.
    ``point``/``vector`` references follow edits until captured by draw.
    Visualization settings are method arguments, not frame state.
    """

    def __init__(
        self,
        origin: Position = (0, 0),
        x_basis: Position | Vector = (1, 0),
        y_basis: Position | Vector = (0, 1),
    ) -> None:
        self._origin = point(origin)
        x = x_basis if isinstance(x_basis, Vector) else point(x_basis)
        y = y_basis if isinstance(y_basis, Vector) else point(y_basis)
        self._x_basis = Vector(x.x, x.y)
        self._y_basis = Vector(y.x, y.y)

    def _matrix(self) -> Transform:
        return (
            Transform()
            if self.description_only or "_entity_state" not in self.__dict__
            else self.snapshot().placed().transform
        )

    def coordinate_matrix(self) -> Transform:
        """Return the current local-to-world matrix, including explicit grouping."""
        x, y, o = self._x_basis, self._y_basis, self._origin
        return self._matrix() @ Transform(x.x, x.y, y.x, y.y, o.x, o.y)

    @property
    def origin(self) -> Point:
        """Return the current world origin, in millimeters."""
        return self._matrix().apply(self._origin)

    @property
    def x_basis(self) -> Vector:
        """Return the current world displacement for one local x unit."""
        return self._matrix().apply_vector(self._x_basis)

    @property
    def y_basis(self) -> Vector:
        """Return the current world displacement for one local y unit."""
        return self._matrix().apply_vector(self._y_basis)

    @property
    def space(self) -> CoordinateSystem:
        """Return a live coordinate adapter for explicit inverse conversions."""
        return FrameSpace(self)

    def point(self, x: float, y: float) -> SpacePoint:
        """Reference a local position; draw captures its current frame state."""
        return SpacePoint(FrameSpace(self), Point(x, y))

    def vector(self, x: float, y: float) -> SpaceVector:
        """Reference a local displacement, unaffected by origin translation."""
        return SpaceVector(FrameSpace(self), Vector(x, y))

    def decompose(self) -> tuple[Drawing, ...]:
        """Emit no painting leaves or visible bounds."""
        return ()

    def anchor(self, name: Anchor = "center") -> AnchorRef:
        """Capture the reference origin without assigning visible bounds."""
        from pdl.scene.references import AnchorRef

        return AnchorRef(Line(self.origin, self.origin), name)

    def move_to(self, end: PointSource) -> Self:
        """Move this frame's origin to a world-space target."""
        from pdl.scene.evaluation import layout_session

        with layout_session() as context:
            target = context.point(end)
        current = self.origin
        return self.translate(target.x - current.x, target.y - current.y)

    def place(self, end: PointSource) -> Self:
        return self.move_to(end)

    def rotate(self, angle: float, *, about: PointSource | None = None) -> Self:
        """Rotate the frame explicitly, defaulting to its own origin."""
        return self._reference_transform(Transform.rotate(angle), about)

    def scale(
        self,
        x: float,
        y: float | None = None,
        *,
        about: PointSource | None = None,
    ) -> Self:
        """Scale the frame explicitly, defaulting to its own origin."""
        return self._reference_transform(Transform.scale(x, y), about)

    def _reference_transform(
        self,
        matrix: Transform,
        about: PointSource | None,
    ) -> Self:
        from pdl.scene.evaluation import layout_session

        with layout_session() as context:
            pivot = context.point(about if about is not None else self.origin)
        return self.apply_transform(matrix.around(pivot))

    def visualize(
        self,
        *,
        axis_length: float = 10,
        origin_radius: float = 0.5,
        x_style: Style | None = None,
        y_style: Style | None = None,
        origin_style: Style | None = None,
    ) -> Group:
        """Create an independent drawable snapshot of axes and an origin marker.

        Args:
            axis_length: Length of each axis in local coordinate units; positive.
            origin_radius: World-space marker radius in millimeters; positive.
            x_style: X-axis paint; defaults to red.
            y_style: Y-axis paint; defaults to blue.
            origin_style: Marker paint; defaults to black fill with no stroke.

        Basis magnitudes affect displayed axes. This method does not change the
        frame, and returned graphics do not follow subsequent frame edits.
        """
        from pdl.geometry.primitives import Circle
        from pdl.scene.composition import Group
        from pdl.scene.paint import BLACK, Color, Style

        if not isfinite(axis_length) or axis_length <= 0:
            raise ValueError("axis_length must be positive and finite.")
        matrix = self.coordinate_matrix()
        origin = matrix.apply((0, 0))
        return Group(
            (
                Line(origin, matrix.apply((axis_length, 0))).set_style(
                    x_style or Style(stroke=Color(0.8, 0.2, 0.2), line_width=0.35)
                ),
                Line(origin, matrix.apply((0, axis_length))).set_style(
                    y_style or Style(stroke=Color(0.2, 0.3, 0.8), line_width=0.35)
                ),
                Circle(origin, origin_radius).set_style(
                    origin_style or Style(stroke=None, fill=BLACK)
                ),
            )
        )


class ReferencePoint(Frame):
    """A non-painting reference position, transformable by Group and Gather.

    Args:
        position: Initial world-space position in millimeters.
    """

    def __init__(self, position: Position = (0, 0)) -> None:
        super().__init__(position)

    @property
    def position(self) -> Point:
        """Return the current world-space reference position."""
        return self.origin


class FrameSpace(CoordinateSystem):
    """Adapt a live Frame to the existing coordinate-reference protocol."""

    source: Frame

    def __init__(self, source: Frame) -> None:
        super().__init__(name="reference")
        object.__setattr__(self, "source", source)

    def __deepcopy__(self, memo: dict[int, object]) -> FrameSpace:
        """Copy mutable reference state instead of sharing an immutable coordinate identity."""
        from copy import deepcopy

        result = FrameSpace(self.source)
        memo[id(self)] = result
        object.__setattr__(result, "source", deepcopy(self.source, memo))
        return result

    def to_world(self) -> Transform:
        return self.source.coordinate_matrix()
