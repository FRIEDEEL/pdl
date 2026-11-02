"""Canvas-owned layer identities, ordering, and weak membership."""

from __future__ import annotations

from typing import Self
from weakref import WeakValueDictionary

from pdl.author.entity.base import Entity
from pdl.author.entity.gather import Gather


def valid_integer(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


class Layer:
    """Stable paint-order identity; never a geometry or transform target."""

    def __init__(self, position: int = 0, *, name: str = "") -> None:
        if not valid_integer(position):
            raise TypeError("Layer position must be an integer.")
        self.initial_position = position
        self.name = name
        self.stack: LayerStack | None = None
        self.registrations: WeakValueDictionary[int, Entity] = WeakValueDictionary()

    def __deepcopy__(self, memo: dict[int, object]) -> Layer:
        return self

    @property
    def position(self) -> int:
        return self.initial_position if self.stack is None else self.stack.index(self)

    @property
    def upper(self) -> Layer | None:
        if self.stack is None or self.position + 1 == len(self.stack):
            return None
        return self.stack[self.position + 1]

    @property
    def lower(self) -> Layer | None:
        return None if self.stack is None or self.position == 0 else self.stack[self.position - 1]

    @property
    def members(self) -> tuple[Entity, ...]:
        return tuple(m for m in self.registrations.values() if m.root is m and m.layer is self)

    def register(self, member: Entity) -> None:
        self.registrations[id(member)] = member

    def unregister(self, member: Entity) -> None:
        self.registrations.pop(id(member), None)

    def add(self, *members: Entity) -> Self:
        for member in members:
            member.set_layer(self)
        return self

    def to_gather(self) -> Gather:
        return Gather(*self.members)


class LayerStack:
    """Canvas-owned bottom-to-top layer identities with list-based insertion.

    Index zero is the bottom layer. Integer assignment binds the current index
    when submitted to Canvas. Missing nonnegative indices are created on demand.
    Negative indices address existing layers using ordinary Python indexing.
    """

    def __init__(self) -> None:
        self._ordered: list[Layer] = []
        self.adopt(Layer())

    def __len__(self) -> int:
        return len(self._ordered)

    def __getitem__(self, index: int) -> Layer:
        if not valid_integer(index):
            raise TypeError("Layer indices must be integers.")
        while index >= len(self._ordered):
            self.adopt(Layer(len(self._ordered)))
        return self._ordered[index]

    def index(self, layer: Layer) -> int:
        return self._ordered.index(layer)

    def adopt(self, layer: Layer) -> Layer:
        """Attach an independent layer; sharing one across canvases is rejected."""
        if layer.stack is not None and layer.stack is not self:
            raise ValueError("A Layer belongs to one Canvas; use a separate Layer for another.")
        if layer not in self._ordered:
            index = max(0, min(layer.initial_position, len(self._ordered)))
            self._ordered.insert(index, layer)
            layer.stack = self
        return layer

    def insert_below(self, reference: Layer, *, name: str = "") -> Layer:
        """Insert a fresh layer immediately below an existing layer."""
        index = self.index(reference)
        layer = Layer(name=name)
        layer.stack = self
        self._ordered.insert(index, layer)
        return layer

    def insert_above(self, reference: Layer, *, name: str = "") -> Layer:
        """Insert a fresh layer immediately above an existing layer."""
        index = self.index(reference)
        layer = Layer(name=name)
        layer.stack = self
        self._ordered.insert(index + 1, layer)
        return layer

    def move_below(self, layer: Layer, reference: Layer) -> None:
        """Move a layer below another, preserving its identity and recorded members."""
        self.index(layer)
        self.index(reference)
        if layer is reference:
            return
        self._ordered.remove(layer)
        self._ordered.insert(self.index(reference), layer)

    def move_above(self, layer: Layer, reference: Layer) -> None:
        """Move a layer above another without altering geometry."""
        self.index(layer)
        self.index(reference)
        if layer is reference:
            return
        self._ordered.remove(layer)
        self._ordered.insert(self.index(reference) + 1, layer)
