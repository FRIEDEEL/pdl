"""Nominal geometry membership is separate from optional capabilities."""

from typing import cast

import pytest

from pdl import Entity
from pdl.author.geometry import Frame, Geometry, Path, Point
from pdl.author.geometry.protocols import PathSource
from pdl.author.transform import Translation


def test_entity_accepts_geometry_without_path_or_measurement_capabilities() -> None:
    class Custom(Geometry):
        pass

    geometry = Custom()
    entity = Entity(geometry)
    assert entity.geometry is geometry
    assert not isinstance(geometry, PathSource)
    assert isinstance(entity.copy().geometry, Custom)
    with pytest.raises(TypeError, match="No bounds query for Custom"):
        _ = entity.bounds


def test_path_conversion_alone_does_not_establish_geometry_membership() -> None:
    class PathConvertible:
        def to_path(self) -> Path:
            return Path().move_to((1, 2)).line_to((3, 4))

    geometry = PathConvertible()
    assert isinstance(geometry, PathSource)
    with pytest.raises(TypeError, match="Entity requires a Geometry instance"):
        Entity(cast(Geometry, geometry))


def test_frame_membership_does_not_require_path_conversion() -> None:
    entity = Entity(Frame((1, 2)))
    entity.apply_transform(Translation(3, 4))
    assert isinstance(entity.geometry, Geometry)
    assert isinstance(entity.geometry, Frame)
    assert entity.geometry.point((0, 0)) == Point(4, 6)
    assert not isinstance(entity.geometry, PathSource)
