"""Identity-based layers and a small ordered layer stack, without spatial transforms."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, Self
from warnings import warn
from weakref import WeakValueDictionary

if TYPE_CHECKING:
    from collections.abc import Iterable

    from pdl.author.composition import Group
    from pdl.author.entity import Entity
    from pdl.author.gather import Gather


class LayerOrder(Protocol):
    """Minimal ordering contract implemented by a canvas-owned stack."""

    def __len__(self) -> int: ...
    def __getitem__(self, index: int) -> Layer: ...
    def index(self, layer: Layer) -> int: ...


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
        self.stack: LayerOrder | None = None
        self.registrations: WeakValueDictionary[int, Entity | Group] = WeakValueDictionary()

    def __deepcopy__(self, memo: dict[int, object]) -> Layer:
        """Keep layer identity when copying graphics, like captured draw records."""
        return self

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
        from pdl.author.gather import Gather

        return Gather(*self.members)


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
