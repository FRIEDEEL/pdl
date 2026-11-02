"""Immediate endpoints, arrowheads, and numerical group edits."""

import pytest

from pdl import Canvas, Group, Style, text
from pdl.author.geometry import Point
from pdl.author.style import Font
from pdl.extensions.diagram import Connection, Node


def test_connection_uses_fixed_anchor_values(font: Font) -> None:
    first = Node(text("A", font), position=(10, 10))
    second = Node(text("B", font), position=(40, 10))
    connection = Connection(first.anchor("east"), second.anchor("west"))
    before = connection.start
    first.translate(5, 0)
    assert connection.start == before
    canvas = Canvas(60, 30).add(connection)
    assert canvas.render().count("<path") == 2
    assert connection.bounds.left == pytest.approx(before.x)
    assert connection.bounds.right == pytest.approx(second.anchor("west").x)


def test_arrow_group_keeps_constant_stroke_width() -> None:
    connection = Connection((0, 0), (10, 0), style=Style(line_width=0.7))
    group = Group(connection)
    canvas = Canvas(50, 30).add(group)
    changed = group.copy().translate(20, 10).scale(2, origin=(20, 10))
    canvas.add(changed)
    assert canvas.render().count('stroke-width="0.7"') == 2
    assert connection.start == Point(0, 0)
    copy = changed.members[0]
    assert isinstance(copy, Connection)
    assert copy.end == Point(40, 10)


def test_degenerate_routes_and_repeated_points() -> None:
    with pytest.raises(ValueError):
        Connection((1, 1), (1, 1))
    assert Connection((0, 0), (5, 0), via=((0, 0),)).via == ()
