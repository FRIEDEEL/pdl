"""Behavioral tests for growing, editable flowcharts."""

from collections.abc import Iterator

import pytest

from pdl import Canvas
from pdl.author.geometry import Point
from pdl.author.style import Font
from pdl.author.style.font_policy import font_context
from pdl.extensions.diagram import Decision, FlowNode, Terminal
from pdl.extensions.diagram.nodes import Node


@pytest.fixture(autouse=True)
def typography(font: Font) -> Iterator[None]:
    with font_context((font,)):
        yield


def placed(root: FlowNode) -> list[Node]:
    return [d for d in root.decompose() if isinstance(d, Node)]


def test_growth_uses_boundary_gap_and_returns_child() -> None:
    root = FlowNode("Root")
    child = FlowNode("A wide process label")
    assert root.right(child, gap=17) is child
    a, b = placed(root)
    assert b.bounds.left - a.bounds.right == pytest.approx(17)
    child.label = "Short"
    a, b = placed(root)
    assert b.bounds.left - a.bounds.right == pytest.approx(17)


@pytest.mark.parametrize("direction", ["left", "right", "above", "below"])
def test_growth_moves_descendants(direction: str) -> None:
    root = FlowNode("Root")
    getattr(root, direction)(Terminal("End"))
    before = [n.bounds.anchor() for n in placed(root)]
    root.translate(8, -4)
    after = [n.bounds.anchor() for n in placed(root)]
    for a, b in zip(before, after, strict=True):
        assert b.x - a.x == pytest.approx(8)
        assert b.y - a.y == pytest.approx(-4)


def test_capture_isolated_from_node_and_edge_edits() -> None:
    root = FlowNode("Root")
    child = root.right(Decision("Valid?"))
    edge = child.connect(root, start="south", end="south", via=((0, -25),))
    canvas = Canvas(100, 80, mode="fit")
    canvas.draw(root)
    before = canvas.render("svg")
    root.translate(5, 8)
    child.label = root.label
    edge.label = "Retry"
    assert canvas.render("svg") == before
    other = Canvas(100, 80, mode="fit")
    other.draw(root)
    assert other.render("svg") != before
    assert "tikzpicture" in other.render("tikz")


def test_merge_and_cycle_keep_existing_positions() -> None:
    root = FlowNode("Root")
    child = root.right(FlowNode("Child"))
    branch = root.above(FlowNode("Branch"))
    before = [n.bounds for n in placed(root)]
    branch.connect(child)
    child.connect(root, start="south", end="south", via=((0, -30),))
    assert [n.bounds for n in placed(root)] == before
    assert len(root.snapshot().edges) == 4
    with pytest.raises(ValueError, match="cycle"):
        child.right(root)
    with pytest.raises(ValueError, match="already"):
        branch.right(child)


@pytest.mark.parametrize("gap", [0, -1, float("inf"), float("nan")])
def test_invalid_gap_rejected(gap: float) -> None:
    with pytest.raises(ValueError, match="Gap"):
        FlowNode("A").right(FlowNode("B"), gap=gap)


def test_diagonal_diamond_port_lies_on_boundary() -> None:
    from pdl.author.geometry.point import Point
    from pdl.author.geometry.shapes import Polygon
    from pdl.extensions.diagram.connections import Connection

    root = Decision("Valid?")
    target = FlowNode("Next", position=(60, 40))
    root.connect(target, start="north east")
    drawings = root.decompose()
    diamond = next(d.geometry for d in drawings if isinstance(d.geometry, Polygon))
    from pdl.author.geometry.queries import bounds_of as bounds

    box = bounds(diamond)
    connection = next(d for d in drawings if isinstance(d, Connection))
    assert isinstance(connection.start, Point)
    assert connection.start.x == pytest.approx(box.anchor().x + box.width / 4)
    assert connection.start.y == pytest.approx(box.anchor().y + box.height / 4)


@pytest.mark.parametrize(
    "start,end", [("east", "north"), ("west", "south"), ("east", "west"), ("south", "south")]
)
def test_default_routes_are_axis_aligned(start: str, end: str) -> None:
    from typing import cast

    from pdl.author.geometry.bounds import Anchor
    from pdl.extensions.diagram.connections import Connection

    root = FlowNode("Root")
    target = FlowNode("Target", position=(65, 35))
    root.connect(target, start=cast(Anchor, start), end=cast(Anchor, end))
    connection = next(d for d in root.decompose() if isinstance(d, Connection))
    points = [connection.start, *connection.via, connection.end]
    for a, b in zip(points, points[1:]):
        assert a.x == pytest.approx(b.x) or a.y == pytest.approx(b.y)


def test_straight_route_and_explicit_waypoints_are_preserved() -> None:
    from pdl.extensions.diagram.connections import Connection

    root = FlowNode("Root")
    target = FlowNode("Target", position=(65, 35))
    edge = root.connect(target, route="straight")
    connection = next(d for d in root.decompose() if isinstance(d, Connection))
    assert connection.via == ()
    edge.route = "orthogonal"
    edge.via = ((25, 15),)
    connection = next(d for d in root.decompose() if isinstance(d, Connection))
    assert connection.via == tuple(Point(*p) for p in edge.via)


def test_directional_growth_keeps_centers_aligned() -> None:
    root = FlowNode("Short")
    child = root.right(Terminal("A longer label"))
    child.above(FlowNode("Review"))
    a, b, c = placed(root)
    assert a.bounds.anchor().y == pytest.approx(b.bounds.anchor().y)
    assert b.bounds.anchor().x == pytest.approx(c.bounds.anchor().x)
