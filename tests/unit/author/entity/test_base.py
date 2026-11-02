"""Direct geometry ownership, explicit sharing, and per-type style fallback."""

from typing import cast

import pytest

from pdl.author.entity.base import Entity
from pdl.author.geometry.path import Path
from pdl.author.geometry.point import Point
from pdl.author.style.color import Color
from pdl.author.style.style import Style


class BlueEntity(Entity):
    default_style = Style(stroke=None, fill=Color(0, 0, 1))


class RedEntity(Entity):
    default_style = Style(stroke=None, fill=Color(1, 0, 0))


def test_constructor_retains_mutable_geometry_without_copying() -> None:
    source = Path().move_to((0, 0))
    entity = Entity(source)
    assert entity.geometry is source
    source.line_to((2, 3))
    assert cast(Path, entity.geometry).current_point == Point(2, 3)
    cast(Path, entity.geometry).line_to((5, 6))
    assert source.current_point == Point(5, 6)


def test_reusing_a_geometry_explicitly_shares_its_edits() -> None:
    source = Path().move_to((0, 0))
    first, second = Entity(source), Entity(source)
    assert first is not second
    assert first.geometry is second.geometry is source
    cast(Path, first.geometry).line_to((10, 20))
    assert cast(Path, second.geometry).current_point == Point(10, 20)


def test_explicit_geometry_copy_provides_independence() -> None:
    source = Path().move_to((0, 0))
    first, second = Entity(source), Entity(source.copy())
    cast(Path, first.geometry).line_to((10, 20))
    assert cast(Path, second.geometry).current_point == Point(0, 0)
    cast(Path, second.geometry).line_to((30, 40))
    assert cast(Path, first.geometry).current_point == Point(10, 20)


def test_reading_a_default_does_not_materialize_instance_style() -> None:
    entity = Entity(Point(1, 2))
    assert entity.style is None
    assert entity.effective_style is Entity.default_style
    assert entity.style is None


def test_type_defaults_are_independent_and_resolved_at_query_time(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    blue, red = BlueEntity(Point(1, 2)), RedEntity(Point(1, 2))
    assert blue.effective_style is BlueEntity.default_style
    assert red.effective_style is RedEntity.default_style
    replacement = Style(stroke=None, fill=Color(0, 1, 0))
    monkeypatch.setattr(BlueEntity, "default_style", replacement)
    assert blue.effective_style is replacement
    assert red.effective_style is RedEntity.default_style
    assert blue.style is None


def test_explicit_style_wins_over_later_class_default_changes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    explicit = Style(stroke=None, fill=None, opacity=0)
    entity = BlueEntity(Point(1, 2), style=explicit)
    monkeypatch.setattr(BlueEntity, "default_style", Style(line_width=3))
    assert entity.style is explicit
    assert entity.effective_style is explicit


def test_set_style_changes_only_the_target_even_with_shared_geometry() -> None:
    source = Path().move_to((1, 2))
    first, second = Entity(source), Entity(source)
    paint = Style(fill=Color(1, 0, 0), line_width=0.5)
    assert first.set_style(paint) is first
    assert first.style is first.effective_style is paint
    assert second.style is None
    assert second.effective_style is Entity.default_style
    assert first.geometry is second.geometry is source


def test_concrete_subclasses_retain_their_type_when_setting_style() -> None:
    entity = BlueEntity(Point(1, 2))
    updated: BlueEntity = entity.set_style(Style(line_width=2))
    assert updated is entity
    assert entity.geometry == Point(1, 2)


def test_geometry_defaults_are_live_without_materializing_style(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from pdl import Text
    from pdl.author.geometry.text import Text as TextGeometry

    text = Text("Default")
    paint = Style(stroke=None, fill=Color(0, 1, 0))
    monkeypatch.setitem(Entity.geometry_defaults, TextGeometry, paint)
    assert text.style is None
    assert text.effective_style is paint
    text.scale(2, 1)
    assert text.style is None
    assert text.effective_style is paint


def test_copy_does_not_confuse_integer_layers_with_geometry_values() -> None:
    from pdl import Circle, Group

    original = Group(Circle((0, 0), 1))
    copied = original.copy()
    assert copied.members[0].reference == Point(0, 0)
    assert copied.members[0].effective_style.stroke == Color(0, 0, 0)
