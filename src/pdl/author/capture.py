"""Mutable authoring handles with isolated captured descriptions."""

from __future__ import annotations

from contextvars import ContextVar
from dataclasses import fields, is_dataclass, replace
from typing import TYPE_CHECKING, Protocol, cast, runtime_checkable

if TYPE_CHECKING:
    pass

from pdl.author.composition import Drawing, Graphic
from pdl.author.entity import Entity
from pdl.author.measurement import layout_session
from pdl.author.spaces import CoordinateSystem
from pdl.foundation.geometry.primitives import Path


@runtime_checkable
class SnapshotProvider(Protocol):
    """Extension hook for capturing editable content without concrete-type dispatch."""

    def snapshot(self) -> Graphic: ...


def description[T](value: T) -> T:
    """Copy local geometry parameters without mutable authoring state."""
    from copy import copy

    result = value.to_path() if isinstance(value, Path) else copy(value)
    if isinstance(result, Entity):
        result.__dict__.pop("_entity_state", None)
        result.__dict__.pop("_reference_frame", None)
        result.description_only = True
    return cast(T, result)


_capture_owners: ContextVar[list[object]] = ContextVar("pdl_capture_owners", default=[])
_capture_memo: ContextVar[dict[int, object] | None] = ContextVar("pdl_capture", default=None)


def capture[T](value: T) -> T:
    """Capture built-in descriptions, sharing immutable values and frame identities.

    Custom Composite implementations must expose immutable descriptions, as
    required by the decomposition protocol. Built-in mutable paths and Entity
    handles are detached recursively.
    """
    current = _capture_memo.get()
    if current is not None:
        return _capture(value, current)
    memo: dict[int, object] = {}
    token = _capture_memo.set(memo)
    owners_token = _capture_owners.set([])
    try:
        return _capture(value, memo)
    finally:
        _capture_memo.reset(token)
        _capture_owners.reset(owners_token)


def _capture[T](value: T, memo: dict[int, object]) -> T:
    # Refreshing authoring descriptions creates temporary objects; retain their
    # owners throughout capture so Python cannot reuse a memoized identity.
    _capture_owners.get().append(value)
    if id(value) in memo:
        return cast(T, memo[id(value)])
    memo[id(value)] = value
    from pdl.author.frames import FrameSpace

    if isinstance(value, FrameSpace):
        result = CoordinateSystem(transform=value.to_world(), name=value.name)
        memo[id(value)] = result
        return cast(T, result)
    if isinstance(value, CoordinateSystem):
        return value
    from pdl.author.composition import Group

    if isinstance(value, SnapshotProvider) and not isinstance(value, Entity):
        return cast(T, value.snapshot())
    if isinstance(value, Group):
        return cast(T, value.snapshot())
    if (
        isinstance(value, Entity)
        and not value.description_only
        and "_entity_state" in value.__dict__
    ):
        result = value.snapshot()
        memo[id(value)] = result
        return cast(T, result)
    if isinstance(value, Path):
        result = value.to_path()
        memo[id(value)] = result
        return cast(T, result)
    if isinstance(value, tuple):
        items = tuple(_capture(item, memo) for item in cast(tuple[object, ...], value))
        result = (
            cast(tuple[object, ...], value)
            if all(a is b for a, b in zip(cast(tuple[object, ...], value), items, strict=True))
            else items
        )
        memo[id(cast(object, value))] = result
        return cast(T, result)
    if is_dataclass(value) and not isinstance(value, type):
        changes: dict[str, object] = {}
        for field in fields(value):
            if field.init:
                original: object = getattr(value, field.name)
                copied = _capture(original, memo)
                if copied is not original:
                    changes[field.name] = copied
        if isinstance(value, Entity):
            from copy import copy

            result = copy(value)
            for name, copied in changes.items():
                setattr(result, name, copied)
            result.description_only = True
        else:
            result = replace(value, **changes) if changes else value
        memo[id(value)] = result
        return cast(T, result)
    return value


def freeze(graphic: Graphic | Drawing) -> Drawing:
    """Capture a draw submission using ordinary author descriptions and fixed layouts.

    Extensions decompose here, before output adapters receive the page. This is
    state capture, not a parallel scene model. Repeated references share one
    measurement context; cyclic composition is rejected.
    """
    from pdl.author.composition import Composite, GroupDescription
    from pdl.author.placement import Placement
    from pdl.author.tex import TeX
    from pdl.author.text import Text

    with layout_session(fresh=True) as context:

        def visit(drawing: Drawing, ancestors: frozenset[int] = frozenset()) -> Drawing:
            drawing = capture(drawing)
            geometry = drawing.geometry
            if id(geometry) in ancestors:
                raise ValueError("Cyclic composite graph during capture.")
            ancestors = ancestors | {id(geometry)}
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
            if isinstance(geometry, (Text, TeX)):
                geometry.capture_layout()
            elif isinstance(geometry, Composite):
                geometry = GroupDescription(
                    tuple(visit(child, ancestors) for child in context.decompose(geometry))
                )
            return Drawing(geometry, drawing.style, drawing.transform)

        root = graphic if isinstance(graphic, Drawing) else Drawing(graphic)
        return visit(capture(root))
