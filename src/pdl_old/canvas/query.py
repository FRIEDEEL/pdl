"""Numerical canvas queries; no independent resolved drawing model."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pdl.author.capture import freeze
from pdl.author.composition import Drawing, Graphic, bounds
from pdl.author.composition import GroupDescription as Group
from pdl.author.measurement import layout_session
from pdl.author.references import PointSource
from pdl.author.spaces import WORLD, CoordinateSystem, SpaceVector
from pdl.author.tex import TeX
from pdl.author.text import Text
from pdl.foundation.geometry.bounds import Bounds
from pdl.foundation.geometry.primitives import Point, Position, Vector

if TYPE_CHECKING:
    from pdl.canvas.canvas import Canvas


class Query:
    """Evaluate only requested values under a canvas's current configuration."""

    def __init__(self, canvas: Canvas) -> None:
        self.canvas = canvas

    def point(self, source: PointSource, *, in_space: CoordinateSystem | None = None) -> Point:
        """Evaluate a point under this canvas's font and coordinate settings.

        Args:
            source: Coordinate pair, numerical Point, or frame-qualified SpacePoint.
            in_space: Target authoring frame. ``None`` uses final Canvas coordinates.

        Returns:
            A fixed numerical Point. The operation does not add objects to the canvas.
            Point queries use only the base mapping when the paint list is empty.
        """
        with self.canvas.evaluation(), layout_session() as context:
            result = context.point(source)
            if in_space is not None:
                return in_space.to_world().inverse().apply(result)
            return self.canvas.viewport().output_transform.apply(result)

    def vector(self, source: SpaceVector, *, in_space: CoordinateSystem | None = None) -> Vector:
        """Measure a frame-qualified displacement in Canvas or authoring coordinates.

        Args:
            source: Vector carrying its source frame.
            in_space: Target authoring frame, or ``None`` for final Canvas coordinates.

        Translation never contributes to the result.
        """
        with self.canvas.evaluation():
            result = source.resolve(WORLD if in_space is None else in_space)
            if in_space is None:
                return self.canvas.viewport().output_transform.apply_vector(result)
            return result

    def bounds(
        self, graphic: Graphic | Drawing, *, in_space: CoordinateSystem | None = None
    ) -> Bounds:
        """Measure axis-aligned layout/geometry bounds, excluding stroke.

        Args:
            graphic: Object or placed Drawing to measure, without drawing it.
            in_space: Authoring frame; ``None`` returns final Canvas coordinates.

        Returns:
            Bounds using current font metrics. With fit/auto-size, the paint list
            defines the viewport; an empty list uses the requested object's bounds.
        """
        with self.canvas.evaluation():
            root = graphic if isinstance(graphic, Drawing) else Drawing(graphic)
            captured = freeze(root)
            transform = (
                in_space.to_world().inverse()
                if in_space is not None
                else self.canvas.viewport(self.canvas.drawings or (root,)).output_transform
            )
            return bounds(Drawing(Group((captured,)), transform=transform))

    def from_canvas(self, position: Position, *, in_space: CoordinateSystem = WORLD) -> Point:
        """Convert a Canvas position back to a fixed authoring point.

        Args:
            position: Numerical point in final Canvas millimeters.
            in_space: Destination authoring frame, default WORLD.

        Returns:
            A numerical point, not a restored dependency or anchor reference.

        Raises:
            ValueError: A required inverse transform is singular.
        """
        with self.canvas.evaluation():
            mapping = self.canvas.viewport().output_transform
            return (in_space.to_world().inverse() @ mapping.inverse()).apply(position)

    def ink_bounds(
        self, graphic: Graphic | Drawing, *, in_space: CoordinateSystem | None = None
    ) -> Bounds:
        """Measure visible glyph contours and shape geometry, excluding stroke."""
        from pdl.author.composition import walk

        with self.canvas.evaluation():
            root = graphic if isinstance(graphic, Drawing) else Drawing(graphic)
            captured = freeze(root)
            leaves: list[Drawing] = []
            for drawing in walk((captured,)):
                geometry = drawing.geometry
                if isinstance(geometry, (Text, TeX)):
                    geometry = geometry.to_path()
                leaves.append(Drawing(geometry, drawing.style, drawing.transform))
            transform = (
                in_space.to_world().inverse()
                if in_space is not None
                else self.canvas.viewport(self.canvas.drawings or (root,)).output_transform
            )
            return bounds(Drawing(Group(tuple(leaves)), transform=transform))
