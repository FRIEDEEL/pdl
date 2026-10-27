"""Editable growing flowcharts, lowered through ordinary pdl components."""

from __future__ import annotations

from dataclasses import dataclass, replace
from math import isfinite
from typing import Literal, Self

from pdl.components.connections import Connection
from pdl.components.nodes import Node
from pdl.geometry.bounds import Anchor
from pdl.geometry.primitives import Point, Polygon, point
from pdl.scene.composition import Drawing
from pdl.scene.evaluation import layout_session
from pdl.scene.paint import BLACK, Style
from pdl.typography.plain import Text
from pdl.typography.tex import TeX

type Direction = Literal["left", "right", "above", "below"]
_PORTS: dict[Direction, tuple[Anchor, Anchor, int, int]] = {
    "left": ("west", "east", -1, 0),
    "right": ("east", "west", 1, 0),
    "above": ("north", "south", 0, 1),
    "below": ("south", "north", 0, -1),
}


class FlowNode:
    """An editable rectangular flow node, with dimensions measured at rendering.

    Args:
        label: Plain string, Text or TeX content.
        position: Initial center in authoring millimeters, used for a root node.
        style: Shape paint.

    Direction methods place a fresh child with a boundary gap (default 12 mm),
    connect it, and return it. Moving a node also moves its grown descendants.
    Use connect for existing nodes and cycles. Draw any node to capture all nodes
    reachable through outgoing edges. Edits affect subsequent captures only.
    """

    kind: Literal["rectangle", "circle", "diamond"] = "rectangle"

    def __init__(
        self,
        label: str | Text | TeX,
        position: tuple[float, float] = (0, 0),
        *,
        style: Style = Style(line_width=0.4),
    ) -> None:
        self.label = label
        self.position = position
        self.style = style
        self.text_style = Style(stroke=None, fill=BLACK)
        self.padding = (3.0, 2.0)
        self.min_width = 18.0
        self.min_height = 10.0
        self._parent: FlowNode | None = None
        self._direction: Direction = "right"
        self._gap = 12.0
        self._edges: list[FlowEdge] = []

    @property
    def label(self) -> Text | TeX:
        """Editable content; assigning a string creates ordinary Text."""
        return self._label

    @label.setter
    def label(self, value: str | Text | TeX) -> None:
        self._label = Text(value) if isinstance(value, str) else value

    def translate(self, x: float, y: float) -> Self:
        """Offset this node and its grown descendants in authoring millimeters."""
        if not all(isfinite(v) for v in (x, y)):
            raise ValueError("Offsets must be finite.")
        self.position = (self.position[0] + x, self.position[1] + y)
        return self

    def _grow(self, child: FlowNode, direction: Direction, gap: float, label: str) -> FlowNode:
        if not isfinite(gap) or gap <= 0:
            raise ValueError("Gap must be positive and finite.")
        ancestor: FlowNode | None = self
        while ancestor is not None:
            if ancestor is child:
                raise ValueError("Growth cannot create a placement cycle; use connect.")
            ancestor = ancestor._parent
        if child._parent is not None:
            raise ValueError("Node already has a growth parent; use connect.")
        child._parent, child._direction, child._gap = self, direction, gap
        start, end, _, _ = _PORTS[direction]
        self.connect(child, start=start, end=end, label=label)
        return child

    def left(self, child: FlowNode, *, gap: float = 12, label: str = "") -> FlowNode:
        """Grow left and return the child; gap is boundary-to-boundary millimeters."""
        return self._grow(child, "left", gap, label)

    def right(self, child: FlowNode, *, gap: float = 12, label: str = "") -> FlowNode:
        """Grow right and return the child."""
        return self._grow(child, "right", gap, label)

    def above(self, child: FlowNode, *, gap: float = 12, label: str = "") -> FlowNode:
        """Grow upward and return the child."""
        return self._grow(child, "above", gap, label)

    def below(self, child: FlowNode, *, gap: float = 12, label: str = "") -> FlowNode:
        """Grow downward and return the child."""
        return self._grow(child, "below", gap, label)

    def connect(
        self,
        target: FlowNode,
        *,
        start: Anchor = "east",
        end: Anchor = "west",
        label: str = "",
        via: tuple[tuple[float, float], ...] = (),
        route: Literal["orthogonal", "straight"] = "orthogonal",
    ) -> FlowEdge:
        """Connect existing nodes without moving them; via uses world millimeters.

        The returned edge exposes editable ports, label, waypoints and style.
        Cardinal ports default to orthogonal elbows; via overrides routing.
        Use route="straight" for a direct segment. No obstacle avoidance is performed.
        """
        edge = FlowEdge(self, target, start, end, label, via, route=route)
        self._edges.append(edge)
        return edge

    def snapshot(self) -> FlowDescription:
        """Capture the outgoing graph and placement ancestors without measuring fonts."""
        nodes: list[FlowNode] = []
        indices: dict[int, int] = {}

        def visit(node: FlowNode) -> None:
            if id(node) in indices:
                return
            indices[id(node)] = len(nodes)
            nodes.append(node)
            if node._parent is not None:
                visit(node._parent)
            for edge in node._edges:
                visit(edge.target)

        visit(self)
        specs = tuple(
            _NodeSpec(
                n.label,
                n.kind,
                n.position,
                n.style,
                n.text_style,
                n.padding,
                n.min_width,
                n.min_height,
                None if n._parent is None else indices[id(n._parent)],
                n._direction,
                n._gap,
            )
            for n in nodes
        )
        edges = tuple(
            _EdgeSpec(
                indices[id(n)],
                indices[id(e.target)],
                e.start,
                e.end,
                e.label,
                e.via,
                e.style,
                e.route,
            )
            for n in nodes
            for e in n._edges
        )
        return FlowDescription(specs, edges)

    def decompose(self) -> tuple[Drawing, ...]:
        return self.snapshot().decompose()


class Decision(FlowNode):
    """A diamond node sized to contain its padded label."""

    kind = "diamond"


class Terminal(FlowNode):
    """A circular start/end node sized to contain its padded label."""

    kind = "circle"


@dataclass
class FlowEdge:
    """Editable directed edge; ports and waypoints are resolved at rendering."""

    source: FlowNode
    target: FlowNode
    start: Anchor = "east"
    end: Anchor = "west"
    label: str = ""
    via: tuple[tuple[float, float], ...] = ()
    style: Style = Style(line_width=0.4)
    route: Literal["orthogonal", "straight"] = "orthogonal"


@dataclass(frozen=True)
class _NodeSpec:
    label: Text | TeX
    kind: Literal["rectangle", "circle", "diamond"]
    offset: tuple[float, float]
    style: Style
    text_style: Style
    padding: tuple[float, float]
    width: float
    height: float
    parent: int | None
    direction: Direction
    gap: float


@dataclass(frozen=True)
class _EdgeSpec:
    source: int
    target: int
    start: Anchor
    end: Anchor
    label: str
    via: tuple[tuple[float, float], ...]
    style: Style
    route: Literal["orthogonal", "straight"]


@dataclass(frozen=True)
class FlowDescription:
    """Immutable flow snapshot; layout uses the eventual typography context."""

    nodes: tuple[_NodeSpec, ...]
    edges: tuple[_EdgeSpec, ...]

    def decompose(self) -> tuple[Drawing, ...]:
        placed: dict[int, Node] = {}

        def place(index: int) -> Node:
            if index in placed:
                return placed[index]
            spec = self.nodes[index]
            node = Node(
                spec.label,
                shape="circle" if spec.kind == "circle" else "rectangle",
                padding=spec.padding,
                min_width=spec.width,
                min_height=spec.height,
                style=spec.style,
                text_style=spec.text_style,
            )
            if spec.kind == "diamond":
                box = node.bounds
                node = Node(
                    spec.label,
                    min_width=box.width * 2,
                    min_height=box.height * 2,
                    style=spec.style,
                    text_style=spec.text_style,
                )
            x, y = spec.offset
            if spec.parent is not None:
                parent = place(spec.parent).bounds
                own = node.bounds
                _, _, dx, dy = _PORTS[spec.direction]
                x += parent.anchor().x + dx * ((parent.width + own.width) / 2 + spec.gap)
                y += parent.anchor().y + dy * ((parent.height + own.height) / 2 + spec.gap)
            node = replace(node, position=(x, y))
            placed[index] = node
            return node

        for i in range(len(self.nodes)):
            place(i)

        def port(index: int, name: Anchor) -> Point:
            node = placed[index]
            with layout_session() as context:
                p = context.point(node.anchor(name))
            if self.nodes[index].kind == "diamond" and " " in name:
                center = node.bounds.anchor()
                return Point((p.x + center.x) / 2, (p.y + center.y) / 2)
            return p

        drawings: list[Drawing] = []
        for edge in self.edges:
            first, last = port(edge.source, edge.start), port(edge.target, edge.end)
            if edge.route not in ("orthogonal", "straight"):
                raise ValueError("Flow edge route must be orthogonal or straight.")
            via = edge.via
            if not via and edge.route == "orthogonal":
                via = _orthogonal(first, last, edge.start, edge.end)
            connection = Connection(first, last, via=via, style=edge.style)
            drawings.append(Drawing(connection))
            if edge.label:
                points = [
                    first,
                    *[point(p) for p in via],
                    last,
                ]
                points = [p for i, p in enumerate(points) if i == 0 or p != points[i - 1]]
                lengths = [
                    ((b.x - a.x) ** 2 + (b.y - a.y) ** 2) ** 0.5 for a, b in zip(points, points[1:])
                ]
                remaining = sum(lengths) / 2
                for a, b, length in zip(points, points[1:], lengths):
                    if remaining <= length:
                        x = a.x + (b.x - a.x) * remaining / length
                        y = a.y + (b.y - a.y) * remaining / length
                        text = Text(edge.label)
                        box = text.layout_bounds
                        nx, ny = -(b.y - a.y) / length, (b.x - a.x) / length
                        distance = abs(nx) * box.width / 2 + abs(ny) * box.height / 2 + 1.5
                        label = Node(
                            text,
                            position=(x + nx * distance, y + ny * distance),
                            padding=(0, 0),
                            style=Style(stroke=None),
                        )
                        drawings.append(Drawing(label))
                        break
                    remaining -= length
        for i, spec in enumerate(self.nodes):
            node = placed[i]
            if spec.kind == "diamond":
                box = node.bounds
                drawings.append(
                    Drawing(
                        Polygon(tuple(box.anchor(a) for a in ("north", "east", "south", "west"))),
                        node.style,
                    )
                )
                drawings.append(node.label_drawing())
            else:
                drawings.append(Drawing(node))
        return tuple(drawings)


def _orthogonal(first: Point, last: Point, start: Anchor, end: Anchor) -> tuple[Point, ...]:
    """Build cardinal-port elbows with short outward stubs, without obstacle search."""
    directions = {"east": (1, 0), "west": (-1, 0), "north": (0, 1), "south": (0, -1)}
    if start not in directions or end not in directions:
        return ()
    sx, sy = directions[start]
    ex, ey = directions[end]
    if (first.y == last.y and sx and ex and sx * (last.x - first.x) > 0 and ex == -sx) or (
        first.x == last.x and sy and ey and sy * (last.y - first.y) > 0 and ey == -sy
    ):
        return ()
    a = Point(first.x + 4 * sx, first.y + 4 * sy)
    b = Point(last.x + 4 * ex, last.y + 4 * ey)
    if bool(sx) != bool(ex):
        elbow = Point(b.x, a.y) if sx else Point(a.x, b.y)
        return a, elbow, b
    if sx:
        x = (a.x + b.x) / 2 if sx != ex else (max(a.x, b.x) + 4 if sx > 0 else min(a.x, b.x) - 4)
        return a, Point(x, a.y), Point(x, b.y), b
    y = (a.y + b.y) / 2 if sy != ey else (max(a.y, b.y) + 4 if sy > 0 else min(a.y, b.y) - 4)
    return a, Point(a.x, y), Point(b.x, y), b
