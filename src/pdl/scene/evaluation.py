"""Per-operation dependency evaluation without a second authoring model."""

from __future__ import annotations

from collections.abc import Callable, Generator
from contextlib import contextmanager
from contextvars import ContextVar
from math import hypot, sqrt
from typing import TYPE_CHECKING, cast

from pdl.geometry.bounds import Bounds, geometry_bounds, transformed_bounds
from pdl.geometry.primitives import Point, point
from pdl.scene.references import AnchorRef, PointSource
from pdl.scene.spaces import SpacePoint

if TYPE_CHECKING:
    from pdl.components.nodes import Node
    from pdl.scene.composition import Composite, Drawing, Graphic


class LayoutContext:
    """Memoize dependencies for one export or explicit measurement operation."""

    def __init__(self) -> None:
        self._values: dict[tuple[str, int, str], object] = {}
        self._owners: dict[int, object] = {}
        self._active: list[tuple[str, int, str]] = []

    def _cached[T](
        self, operation: str, owner: object, compute: Callable[[], T], detail: str = ""
    ) -> T:
        key = (operation, id(owner), detail)
        self._owners[id(owner)] = owner
        if key in self._values:
            return cast(T, self._values[key])
        if key in self._active:
            chain = self._active[self._active.index(key) :] + [key]
            labels = [
                f"{type(self._owners[identity]).__name__}.{op}({name})"
                for op, identity, name in chain
            ]
            raise ValueError("Cyclic layout dependency: " + " -> ".join(labels))
        self._active.append(key)
        try:
            result = compute()
            self._values[key] = result
            return result
        finally:
            self._active.pop()

    def point(self, source: PointSource) -> Point:
        if isinstance(source, SpacePoint):
            return source.resolve()
        if not isinstance(source, AnchorRef):
            return point(source)
        anchor = self.anchor(source)
        offset = point(source.offset)
        x, y = anchor.x + offset.x, anchor.y + offset.y
        for vector in source.vector_offsets:
            resolved = vector.resolve()
            x += resolved.x
            y += resolved.y
        return Point(x, y)

    def anchor(self, reference: AnchorRef) -> Point:
        from pdl.components.nodes import Node
        from pdl.scene.authoring import Placement
        from pdl.scene.composition import Drawing

        target, name = reference.target, reference.name

        def compute() -> Point:
            if isinstance(target, Placement):
                return self.point(AnchorRef(target.placed(), name))
            if isinstance(target, Drawing):
                local = self.point(AnchorRef(target.geometry, name))
                return target.transform.apply(local)
            box = self.bounds(target)
            result = box.anchor(name)
            if isinstance(target, Node) and target.shape == "circle" and " " in name:
                center = box.anchor()
                return Point(
                    center.x + (result.x - center.x) / sqrt(2),
                    center.y + (result.y - center.y) / sqrt(2),
                )
            return result

        return self._cached("anchor", target, compute, name)

    def node_bounds(self, node: Node) -> Bounds:
        def compute() -> Bounds:
            label = node.label.layout_bounds
            width = max(node.min_width, label.width + 2 * node.padding[0])
            height = max(node.min_height, label.height + 2 * node.padding[1])
            if node.shape == "circle":
                width = height = max(
                    hypot(label.width + 2 * node.padding[0], label.height + 2 * node.padding[1]),
                    node.min_width,
                    node.min_height,
                )
            position = self.point(node.position)
            return Bounds(
                position.x - width / 2,
                position.y - height / 2,
                position.x + width / 2,
                position.y + height / 2,
            )

        return self._cached("bounds", node, compute)

    def decompose(self, graphic: Composite) -> tuple[Drawing, ...]:
        return self._cached("decompose", graphic, graphic.decompose)

    def bounds(self, graphic: Graphic | Drawing) -> Bounds:
        from pdl.components.nodes import Node
        from pdl.scene.composition import Composite, Drawing
        from pdl.typography.plain import Text
        from pdl.typography.tex import TeX

        if isinstance(graphic, Node):
            return self.node_bounds(graphic)

        def compute() -> Bounds:
            if isinstance(graphic, Drawing):
                return self._drawing_bounds(graphic)
            if isinstance(graphic, Composite):
                result: Bounds | None = None
                for child in self.decompose(graphic):
                    box = self._drawing_bounds(child)
                    result = box if result is None else result.union(box)
                return result if result is not None else Bounds.empty()
            if isinstance(graphic, (Text, TeX)):
                return graphic.layout_bounds
            return geometry_bounds(graphic)

        return self._cached("bounds", graphic, compute)

    def _drawing_bounds(self, drawing: Drawing, ancestors: frozenset[int] = frozenset()) -> Bounds:
        from pdl.scene.composition import Composite, Drawing
        from pdl.typography.plain import Text
        from pdl.typography.tex import TeX

        geometry = drawing.geometry
        if isinstance(geometry, Composite):
            if id(geometry) in ancestors:
                raise ValueError(f"Cyclic composite graph: {type(geometry).__name__}.")

            # Keep exact path extrema through nested placements rather than
            # transforming an already axis-aligned bounding rectangle.
            def compute() -> Bounds:
                result: Bounds | None = None
                for child in self.decompose(geometry):
                    box = self._drawing_bounds(
                        Drawing(child.geometry, child.style, drawing.transform @ child.transform),
                        ancestors | {id(geometry)},
                    )
                    result = box if result is None else result.union(box)
                return result if result is not None else Bounds.empty()

            return self._cached("placed bounds", geometry, compute, str(drawing.transform.values))
        if isinstance(geometry, (Text, TeX)):
            return self.bounds(geometry).transformed(drawing.transform)
        return transformed_bounds(geometry, drawing.transform)


_current: ContextVar[LayoutContext | None] = ContextVar("pdl_layout", default=None)


@contextmanager
def layout_session(*, fresh: bool = False) -> Generator[LayoutContext, None, None]:
    """Reuse a nested operation's context, or isolate a new render invocation."""
    current = _current.get()
    if current is not None and not fresh:
        yield current
        return
    context = LayoutContext()
    token = _current.set(context)
    try:
        yield context
    finally:
        _current.reset(token)
