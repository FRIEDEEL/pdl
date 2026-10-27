"""Behavioral tests for growing, editable flowcharts."""

from collections.abc import Iterator

import pytest

from pdl import Canvas, Decision, FlowNode, Font, Terminal
from pdl.components.nodes import Node
from pdl.typography.plain import font_context


@pytest.fixture(autouse=True)
def typography(font: Font) -> Iterator[None]:
    with font_context((font,)):
        yield


def placed(root: FlowNode) -> list[Node]:
    return [d.geometry for d in root.decompose() if isinstance(d.geometry, Node)]


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
    from pdl.components.connections import Connection
    from pdl.geometry.primitives import Point, Polygon

    root = Decision("Valid?")
    target = FlowNode("Next", position=(60, 40))
    root.connect(target, start="north east")
    drawings = root.decompose()
    diamond = next(d.geometry for d in drawings if isinstance(d.geometry, Polygon))
    from pdl.scene.composition import bounds

    box = bounds(diamond)
    connection = next(d.geometry for d in drawings if isinstance(d.geometry, Connection))
    assert isinstance(connection.start, Point)
    assert connection.start.x == pytest.approx(box.anchor().x + box.width / 4)
    assert connection.start.y == pytest.approx(box.anchor().y + box.height / 4)
