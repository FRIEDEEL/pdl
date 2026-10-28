"""Concrete geometry snapshots and independent authoring queries."""

from __future__ import annotations

from dataclasses import dataclass, fields, replace
from typing import TYPE_CHECKING

from pdl.geometry.bounds import Anchor, Bounds
from pdl.geometry.primitives import Point, Position, Vector
from pdl.scene.composition import Composite, Drawing, Graphic, bounds
from pdl.scene.composition import GroupDescription as Group
from pdl.scene.evaluation import layout_session
from pdl.scene.references import AnchorRef, PointSource
from pdl.scene.spaces import WORLD, CoordinateSystem, SpaceVector
from pdl.typography.plain import Text, TextLayout
from pdl.typography.tex import TeX, TeXLayout

if TYPE_CHECKING:
    from pdl.scene.canvas import Canvas


@dataclass(kw_only=True)
class MeasuredText(Text):
    """Text retaining native identity with a fixed shaping result."""

    measured: TextLayout

    @property
    def layout(self) -> TextLayout:
        return self.measured


@dataclass(kw_only=True)
class MeasuredTeX(TeX):
    """TeX retaining source identity and a fixed measured fragment."""

    measured: TeXLayout

    @property
    def layout(self) -> TeXLayout:
        return self.measured


@dataclass(frozen=True)
class ResolvedGraphic:
    """A detached geometry snapshot with no font or position dependencies.

    Native shape, node and text identity is retained. All typography metrics
    and position references are fixed; output adapters may lower as needed.
    """

    _drawings: tuple[Drawing, ...]

    def decompose(self) -> tuple[Drawing, ...]:
        # Never expose mutable paths owned by the snapshot.
        from pdl.scene.authoring import capture

        return capture(self._drawings)

    def bounds(self) -> Bounds:
        """Return fixed axis-aligned layout bounds, excluding stroke."""
        return bounds(Group(self.decompose()))

    def anchor(self, name: Anchor = "center") -> Point:
        """Return a numerical shape anchor, or bounds anchor for multiple drawings."""
        with layout_session() as context:
            if len(self._drawings) == 1:
                return context.point(AnchorRef(self._drawings[0], name))
            return self.bounds().anchor(name)


class Query:
    """Evaluate only requested values under a canvas's current configuration."""

    def __init__(self, canvas: Canvas) -> None:
        self.canvas = canvas

    def point(self, source: PointSource, *, in_space: CoordinateSystem | None = None) -> Point:
        """Evaluate a point under this canvas's font and coordinate settings.

        Args:
            source: Coordinate pair, Point, SpacePoint, or deferred AnchorRef.
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
            resolved = resolve_geometry(root)
            transform = (
                in_space.to_world().inverse()
                if in_space is not None
                else self.canvas.viewport(self.canvas.drawings or (root,)).output_transform
            )
            return bounds(Drawing(Group(resolved.decompose()), transform=transform))

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
        from pdl.scene.composition import walk

        with self.canvas.evaluation():
            root = graphic if isinstance(graphic, Drawing) else Drawing(graphic)
            resolved = resolve_geometry(root)
            leaves: list[Drawing] = []
            for drawing in walk(resolved.decompose()):
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


def resolve_geometry(graphic: Graphic | Drawing) -> ResolvedGraphic:
    """Resolve dependencies without discarding native shape and node identity."""
    from pdl.components.nodes import Node
    from pdl.scene.authoring import Around, Entity, Placement, capture, description

    with layout_session() as context:

        def measured(label: Text | TeX) -> Text | TeX:
            if isinstance(label, (MeasuredText, MeasuredTeX)):
                return label
            if isinstance(label, Text):
                return MeasuredText(
                    **{f.name: getattr(label, f.name) for f in fields(Text)}, measured=label.layout
                )
            return MeasuredTeX(
                source=label.source,
                size=label.size,
                position=label.position,
                config=label.environment,
                measured=label.layout,
            )

        def visit(drawing: Drawing, ancestors: frozenset[int] = frozenset()) -> Drawing:
            geometry = drawing.geometry
            if id(geometry) in ancestors:
                raise ValueError("Cyclic composite graph during resolution.")
            ancestors = ancestors | {id(geometry)}
            if isinstance(geometry, Entity) and not geometry.description_only:
                geometry = (
                    geometry.snapshot()
                    if type(geometry) is Entity or "_entity_state" in geometry.__dict__
                    else description(geometry)
                )
            if isinstance(geometry, Around):
                child = geometry.decompose()[0]
                return visit(
                    Drawing(
                        child.geometry,
                        drawing.style if drawing.style is not None else child.style,
                        drawing.transform @ child.transform,
                    ),
                    ancestors,
                )
            if isinstance(geometry, Placement):
                placed = geometry.placed()
                return visit(
                    Drawing(
                        placed.geometry,
                        drawing.style if drawing.style is not None else placed.style,
                        drawing.transform @ placed.transform,
                    ),
                    ancestors,
                )
            if isinstance(geometry, Node):
                context.bounds(geometry)
                geometry = replace(
                    geometry,
                    label=measured(geometry.label),
                    position=context.point(geometry.position),
                )
            elif isinstance(geometry, (Text, TeX)):
                geometry = measured(geometry)
            elif isinstance(geometry, Composite):
                geometry = Group(
                    tuple(visit(child, ancestors) for child in context.decompose(geometry))
                )
            if isinstance(geometry, Entity):
                geometry.description_only = True
            return Drawing(capture(geometry), drawing.style, drawing.transform)

        root = graphic if isinstance(graphic, Drawing) else Drawing(graphic)
        return ResolvedGraphic((visit(root),))
