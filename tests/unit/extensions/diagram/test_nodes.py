"""Content-sized node layout and boundary anchors."""

from math import hypot

import pytest

from pdl.author.entity.base import Entity
from pdl.author.entity.factories import text
from pdl.author.geometry import Point
from pdl.author.geometry.bounds import Bounds
from pdl.author.style.font import Font
from pdl.extensions.diagram.nodes import Node


def bounds(value: Entity) -> Bounds:
    return value.bounds


def test_node_contains_label_layout_and_padding(font: Font) -> None:
    label = text("Pump\nP1", font, position=(100, 100))
    node = Node(label, position=(20, 30), padding=(3, 2))
    assert node.bounds.width == pytest.approx(label.bounds.width + 6)
    assert node.bounds.height == pytest.approx(label.bounds.height + 4)
    assert node.anchor() == Point(20, 30)
    assert bounds(node) == node.bounds
    assert label.reference == Point(100, 100)


def test_circular_diagonal_anchor_is_on_circle(font: Font) -> None:
    node = Node(text("P", font), shape="circle")
    anchor = node.anchor("north east")
    assert hypot(anchor.x, anchor.y) == pytest.approx(node.bounds.width / 2)
