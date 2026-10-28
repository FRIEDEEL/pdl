"""Per-operation dependency evaluation without a second authoring model."""

from __future__ import annotations

from collections.abc import Callable, Generator
from contextlib import contextmanager
from contextvars import ContextVar
from typing import TYPE_CHECKING, Protocol, cast, runtime_checkable

from pdl.author.references import AnchorQuery, PointSource
from pdl.author.spaces import SpacePoint
from pdl.foundation.geometry.bounds import Anchor, Bounds, geometry_bounds, transformed_bounds
from pdl.foundation.geometry.primitives import Point, point

if TYPE_CHECKING:
    from pdl.author.composition import Composite, Drawing, Graphic


@runtime_checkable
class LocalBounds(Protocol):
    """An object with measured local layout bounds."""

    @property
    def layout_bounds(self) -> Bounds: ...


@runtime_checkable
class LocalAnchor(Protocol):
    """Optional shape-specific numerical anchor calculation."""

    def local_anchor(self, name: Anchor = "center") -> Point: ...


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

    def point(self, source: PointSource | AnchorQuery) -> Point:
        if isinstance(source, SpacePoint):
            return source.resolve()
        if not isinstance(source, AnchorQuery):
            return point(source)
        return self.anchor(source)

    def anchor(self, reference: AnchorQuery) -> Point:
        from pdl.author.composition import Drawing
        from pdl.author.placement import Placement

        target, name = reference.target, reference.name

        def compute() -> Point:
            if isinstance(target, Placement):
                return self.point(AnchorQuery(target.placed(), name))
            if isinstance(target, Drawing):
                local = self.point(AnchorQuery(target.geometry, name))
                return target.transform.apply(local)
            if isinstance(target, LocalAnchor):
                return target.local_anchor(name)
            box = self.bounds(target)
            result = box.anchor(name)
            return result

        return self._cached("anchor", target, compute, name)

    def decompose(self, graphic: Composite) -> tuple[Drawing, ...]:
        return self._cached("decompose", graphic, graphic.decompose)

    def bounds(self, graphic: Graphic | Drawing) -> Bounds:
        from pdl.author.capture import capture
        from pdl.author.composition import Composite, Drawing
        from pdl.author.entity import Entity

        if (
            isinstance(graphic, Entity)
            and not graphic.description_only
            and ("_entity_state" in graphic.__dict__ or type(graphic).__name__ == "Group")
        ):
            return self.bounds(capture(graphic))

        def compute() -> Bounds:
            if isinstance(graphic, Drawing):
                return self._drawing_bounds(graphic)
            if isinstance(graphic, Composite):
                result: Bounds | None = None
                for child in self.decompose(graphic):
                    box = self._drawing_bounds(child)
                    result = box if result is None else result.union(box)
                return result if result is not None else Bounds.empty()
            if isinstance(graphic, LocalBounds):
                return graphic.layout_bounds
            return geometry_bounds(graphic)

        return self._cached("bounds", graphic, compute)

    def _drawing_bounds(self, drawing: Drawing, ancestors: frozenset[int] = frozenset()) -> Bounds:
        from pdl.author.composition import Composite, Drawing

        geometry = drawing.geometry
        from pdl.author.capture import capture
        from pdl.author.entity import Entity

        if (
            isinstance(geometry, Entity)
            and not geometry.description_only
            and ("_entity_state" in geometry.__dict__ or type(geometry).__name__ == "Group")
        ):
            return self._drawing_bounds(
                Drawing(capture(geometry), drawing.style, drawing.transform), ancestors
            )

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
        if isinstance(geometry, LocalBounds):
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
