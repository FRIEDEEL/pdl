"""Shared selections are flat and apply each command once per operation unit."""

import pytest

from pdl import Canvas, Circle, Entity, Gather, Group, Point


def test_overlapping_gathers_and_flattened_membership() -> None:
    a, b, c = (Entity(Circle((0, 0), 1)) for _ in range(3))
    first, second = Gather(a, b), Gather(a, c)
    flat = Gather(first, second)
    first.translate(10, 0)
    second.translate(0, 20)
    query = Canvas(100, 100).query()
    assert query.point(a.anchor()) == Point(10, 20)
    assert flat.members == (a, b, c)
    first.remove(b)
    flat.translate(1, 0)
    assert query.point(b.anchor()) == Point(11, 0)
    assert first.intersection(second).members == (a,)
    assert flat.difference(first).members == (b, c)


def test_selection_promotes_and_deduplicates_after_regrouping() -> None:
    a, b = Entity(Circle((0, 0), 1)), Entity(Circle((10, 0), 1))
    selection = Gather(a, b)
    group = Group((a, b))
    with pytest.warns(UserWarning, match="promoted"):
        selection.translate(20, 0)
    assert Canvas(100, 100).query().point(a.anchor()) == Point(20, 0)
    with pytest.warns(UserWarning, match="promoted"):
        explicit = Gather(a, group)
    assert explicit.members == (group,)
