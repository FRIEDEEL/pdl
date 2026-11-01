"""Content-sized node layout and boundary anchors."""

from math import hypot

import pytest

from pdl import Point
from pdl.author.composition import bounds
from pdl.author.measurement import layout_session
from pdl.author.text import Text
from pdl.extensions.diagrams.nodes import Node
from pdl.foundation.typography.shaping import Font


def test_node_contains_label_layout_and_padding(font: Font) -> None:
    label = Text("Pump\nP1", font, position=(100, 100))
    node = Node(label, position=(20, 30), padding=(3, 2))
    assert node.bounds.width == pytest.approx(label.layout_bounds.width + 6)
    assert node.bounds.height == pytest.approx(label.layout_bounds.height + 4)
    with layout_session() as context:
        assert context.point(node.anchor()) == Point(20, 30)
    assert bounds(node) == node.bounds
    assert label.position == (100, 100)


def test_circular_diagonal_anchor_is_on_circle(font: Font) -> None:
    node = Node(Text("P", font), shape="circle")
    with layout_session() as context:
        anchor = context.point(node.anchor("north east"))
    assert hypot(anchor.x, anchor.y) == pytest.approx(node.bounds.width / 2)
