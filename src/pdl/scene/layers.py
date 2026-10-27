"""Identity-based layers and a small ordered layer stack, without spatial transforms."""

from __future__ import annotations

from typing import TYPE_CHECKING, Self
from warnings import warn
from weakref import WeakValueDictionary

if TYPE_CHECKING:
    from collections.abc import Iterable

    from pdl.scene.authoring import Entity
    from pdl.scene.composition import Group
    from pdl.scene.gather import Gather


class Layer:
    """A stable layer identity with no geometry or transformation.

    Args:
        position: Initial position when adopted by a Canvas layer stack.
        name: Optional reader-facing label.

    Higher positions paint later. Use ``canvas.layers[index]`` for canonical
    integer lookup; independent Layer instances never share global membership.
    Layer assignment does not submit a drawing. Members are weakly referenced.
    """

    def __init__(self, position: int = 0, *, name: str = "") -> None:
        if not valid_integer(position):
            raise TypeError("Layer position must be an integer.")
        self.initial_position = position
        self.name = name
        self.stack: LayerStack | None = None
        self.registrations: WeakValueDictionary[int, Entity | Group] = WeakValueDictionary()

    @property
    def position(self) -> int:
        """Current stack position, or the initial position before adoption."""
        return self.initial_position if self.stack is None else self.stack.index(self)

    @property
    def upper(self) -> Layer | None:
        """Return the immediately higher layer, without creating one.

        Returns:
            The current neighbor, or None at the top or before stack adoption.
            Inserting or moving layers changes subsequent reads.
        """
        if self.stack is None:
            return None
        index = self.stack.index(self) + 1
        return self.stack[index] if index < len(self.stack) else None

    @property
    def lower(self) -> Layer | None:
        """Return the immediately lower layer, without creating one.

        Returns:
            The current neighbor, or None at the bottom or before stack adoption.
            This never wraps around through negative indexing.
        """
        if self.stack is None:
            return None
        index = self.stack.index(self) - 1
        return self.stack[index] if index >= 0 else None

    @property
    def members(self) -> tuple[Entity | Group, ...]:
        """Return live outermost members, excluding objects subsequently regrouped."""
        return tuple(m for m in self.registrations.values() if m.root is m and m.layer is self)

    def add(self, *members: Entity | Group) -> Self:
        """Assign instances to this layer, promoting grouped children with a warning."""
        for member in members:
            assign_layer(member, self)
        return self

    def to_gather(self) -> Gather:
        """Capture current top-level members as an independent operation set."""
        from pdl.scene.gather import Gather

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


def assign_layer(member: Entity | Group, layer: int | Layer) -> None:
    """Assign only a top-level unit; layer changes affect subsequent draw captures."""
    if not valid_layer(layer):
        raise TypeError("Expected an integer layer index or Layer instance.")
    root = member.root
    if root is not member:
        warn("Layer target promoted to its outermost Group.", UserWarning, stacklevel=3)
    old = root.assigned_layer
    if isinstance(old, Layer):
        old.registrations.pop(id(root), None)
    root.assigned_layer = layer
    if isinstance(layer, Layer):
        layer.registrations[id(root)] = root


def highest_layer(members: Iterable[Entity | Group]) -> int | Layer:
    """Choose the uppermost member layer; empty assemblies start at index zero."""
    layers = [member.layer for member in members]
    stacks = {layer.stack for layer in layers if isinstance(layer, Layer) and layer.stack}
    if len(stacks) > 1:
        raise ValueError("Cannot combine members from different Canvas layer stacks.")
    return max(layers, key=layer_position, default=0)


def layer_position(layer: int | Layer) -> int:
    return layer if isinstance(layer, int) else layer.position


def valid_integer(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def valid_layer(value: object) -> bool:
    return valid_integer(value) or isinstance(value, Layer)
