"""Direct geometry ownership, explicit sharing, and per-type style fallback."""

import pytest

from pdl.author.entity.base import Entity
from pdl.author.geometry.path import Path
from pdl.author.geometry.point import Point
from pdl.author.style.color import Color
from pdl.author.style.style import Style


class BlueEntity(Entity[Point]):
    default_style = Style(stroke=None, fill=Color(0, 0, 1))


class RedEntity(Entity[Point]):
    default_style = Style(stroke=None, fill=Color(1, 0, 0))


def test_constructor_retains_mutable_geometry_without_copying() -> None:
    source = Path().move_to((0, 0))
    entity = Entity(source)
    assert entity.geometry is source
    source.line_to((2, 3))
    assert entity.geometry.current_point == Point(2, 3)
    entity.geometry.line_to((5, 6))
    assert source.current_point == Point(5, 6)


def test_reusing_a_geometry_explicitly_shares_its_edits() -> None:
    source = Path().move_to((0, 0))
    first, second = Entity(source), Entity(source)
    assert first is not second
    assert first.geometry is second.geometry is source
    first.geometry.line_to((10, 20))
    assert second.geometry.current_point == Point(10, 20)


def test_explicit_geometry_copy_provides_independence() -> None:
    source = Path().move_to((0, 0))
    first, second = Entity(source), Entity(source.copy())
    first.geometry.line_to((10, 20))
    assert second.geometry.current_point == Point(0, 0)
    second.geometry.line_to((30, 40))
    assert first.geometry.current_point == Point(10, 20)


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
