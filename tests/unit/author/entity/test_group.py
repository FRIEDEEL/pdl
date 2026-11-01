"""Ownership, nested fallback, and explicit selection semantics."""

import pytest

from pdl.author.entity.base import Entity
from pdl.author.entity.gather import Gather
from pdl.author.entity.group import Group
from pdl.author.geometry.point import Point
from pdl.author.style.style import Style


def test_group_never_writes_inherited_style_into_member() -> None:
    member = Entity(Point(1, 2))
    style = Style(line_width=4)
    group = Group(member, style=style)
    assert member.style is None
    assert member.effective_style is style
    group.set_style(Style(line_width=8))
    assert member.style is None
    assert member.effective_style.line_width == 8
    group.remove(member)
    assert member.style is None
    assert member.effective_style is Entity.default_style


def test_nested_style_and_gather_update_exact_targets() -> None:
    first, second = Entity(Point(0, 0)), Entity(Point(1, 0), style=Style(line_width=2))
    inner = Group(first, second)
    outer = Group(inner, style=Style(line_width=4))
    assert first.effective_style.line_width == 4
    inner.set_style(Style(line_width=6))
    assert first.effective_style.line_width == 6
    assert second.effective_style.line_width == 2
    Gather(inner).set_style(Style(line_width=8))
    assert first.style is None
    assert second.style is not None and second.style.line_width == 2
    outer.remove(inner)
    inner.remove(first)
    assert first.effective_style is Entity.default_style


def test_cycles_and_multiple_parents_are_rejected_before_mutation() -> None:
    member = Entity(Point(0, 0))
    inner = Group(member)
    outer = Group(inner)
    with pytest.raises(ValueError):
        inner.add(outer)
    with pytest.raises(ValueError):
        Group().add(member)
    assert member.parent is inner
    assert inner.parent is outer


def test_copy_detaches_root_but_preserves_copied_child_ownership() -> None:
    original = Group(Entity(Point(0, 0)), style=Style(line_width=3))
    copy = original.copy()
    assert copy.parent is None
    assert copy.members[0] is not original.members[0]
    assert copy.members[0].parent is copy
    assert copy.members[0].effective_style == original.style
