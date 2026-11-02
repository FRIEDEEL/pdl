"""Immediate geometry replacement, pivot behavior, and explicit stroke scaling."""

import pytest

from pdl.author.entity.base import Entity
from pdl.author.entity.gather import Gather
from pdl.author.entity.group import Group
from pdl.author.geometry.base import Geometry
from pdl.author.geometry.path import Path
from pdl.author.geometry.point import Point
from pdl.author.geometry.shapes import Circle, Rectangle
from pdl.author.style.style import Style
from pdl.author.transform.affine import Rescale, Scaling


def test_circle_stretch_replaces_only_target_geometry() -> None:
    geometry = Circle((5, 6), 2)
    first, second = Entity(geometry), Entity(geometry)
    first.scale(2, 1)
    assert isinstance(first.geometry, Path)
    assert second.geometry is geometry
    assert first.reference == Point(5, 6)
    assert first.bounds.left == pytest.approx(1)
    assert first.bounds.right == pytest.approx(9)
    assert first.bounds.top == pytest.approx(8)


def test_uniform_scale_preserves_circle_and_default_stroke() -> None:
    entity = Entity(Circle((10, 20), 2), style=Style(line_width=3))
    entity.rescale(2)
    assert isinstance(entity.geometry, Circle)
    assert entity.geometry.radius == 4
    assert entity.reference == Point(10, 20)
    assert entity.effective_style.line_width == 3


def test_rescale_keeps_explicit_linewidth_option_with_pivot() -> None:
    entity = Entity(Circle((10, 20), 2), style=Style(line_width=3))
    Rescale(-2, include_linewidth=True).around((10, 20)).apply_to(entity)
    assert entity.reference == Point(10, 20)
    assert entity.effective_style.line_width == 6
    with pytest.raises(TypeError):
        Scaling(2, 1, include_linewidth=True)  # type: ignore[call-arg]


def test_transforms_do_not_save_cumulative_matrices() -> None:
    entity = Entity(Rectangle((2, 3), 4, 5))
    entity.translate(7, 9)
    assert isinstance(entity.geometry, Rectangle)
    assert entity.geometry.origin == Point(9, 12)
    assert not hasattr(entity, "transform")
    entity.move_to((0, 0))
    assert entity.reference == Point(0, 0)


def test_group_reference_and_members_transform_together() -> None:
    first, second = Entity(Circle((0, 0), 1)), Entity(Circle((4, 0), 1))
    group = Group(first, second, reference=(2, 0))
    group.rotate(90)
    assert first.reference.x == pytest.approx(2)
    assert first.reference.y == pytest.approx(-2)
    assert second.reference.y == pytest.approx(2)
    assert group.reference == Point(2, 0)


def test_gather_deduplicates_group_and_selected_child() -> None:
    child = Entity(Circle((1, 0), 1))
    group = Group(child)
    Gather(child, group).translate(3, 0)
    assert child.reference == Point(4, 0)


def test_group_conversion_failure_is_atomic() -> None:
    first, unsupported = Entity(Circle((1, 0), 1)), Entity(Geometry())
    group = Group(first, unsupported)
    with pytest.raises(TypeError):
        group.translate(3, 0)
    assert first.reference == Point(1, 0)
    assert group.reference == Point(0, 0)


def test_gather_linewidth_uses_existing_parent_fallback() -> None:
    child = Entity(Circle((1, 0), 1))
    Group(child, style=Style(line_width=3))
    Gather(child).apply_transform(Rescale(2, include_linewidth=True))
    assert child.effective_style.line_width == 6
