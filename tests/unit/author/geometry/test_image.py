"""Captured raster bytes survive source changes and affine viewport edits."""

import base64
from pathlib import Path

import pytest

from pdl.author.entity.base import Entity
from pdl.author.geometry.image import Image
from pdl.author.geometry.point import Point

PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jO9sAAAAASUVORK5CYII="
)


def test_affine_image_keeps_pixels_and_bakes_viewport_corners(tmp_path: Path) -> None:
    source = tmp_path / "image.png"
    source.write_bytes(PNG)
    geometry = Image(source, 10, 5, position=(2, 3))
    source.unlink()
    entity = Entity(geometry).rotate(90)
    assert isinstance(entity.geometry, Image)
    assert entity.geometry.data == PNG
    assert entity.geometry.pixel_width == 1
    assert entity.reference == Point(2, 3)
    assert entity.bounds.width == pytest.approx(5)
    assert entity.bounds.height == pytest.approx(10)
    assert entity.geometry.asset(tmp_path).read_bytes() == PNG
