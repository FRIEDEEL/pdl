"""Explicit connector endpoints, arrowheads and composite placement."""

import pytest

from pdl import Canvas, Style
from pdl.author.composition import Drawing, Group, bounds
from pdl.author.measurement import layout_session
from pdl.author.text import Text
from pdl.extensions.diagrams.connections import Connection
from pdl.extensions.diagrams.nodes import Node
from pdl.foundation.geometry.transforms import Transform
from pdl.foundation.typography.shaping import Font


def test_connection_anchor_references_and_arrow_bounds(font: Font) -> None:
    first = Node(Text("A", font), position=(10, 10))
    second = Node(Text("B", font), position=(40, 10))
    connection = Connection(first.anchor("east"), second.anchor("west"))
    canvas = Canvas(60, 30)
    canvas.draw(connection)
    assert canvas.render().count("<path") == 2
    with layout_session() as context:
        assert bounds(connection).left == pytest.approx(context.point(first.anchor("east")).x)
        assert bounds(connection).right == pytest.approx(context.point(second.anchor("west")).x)


def test_group_instances_keep_styles_and_fixed_width() -> None:
    connection = Connection((0, 0), (10, 0), style=Style(line_width=0.7))
    group = Group((Drawing(connection),))
    canvas = Canvas(50, 30)
    canvas.draw(group)
    canvas.draw(group.transformed(Transform.translate(20, 10) @ Transform.scale(2)))
    assert canvas.render().count('stroke-width="0.7"') == 2
    assert bounds(group).anchor("west").x == 0


def test_degenerate_connector() -> None:
    with pytest.raises(ValueError):
        Connection((1, 1), (1, 1))
    assert Connection((0, 0), (5, 0), via=((0, 0),)).decompose()
