"""Real XeLaTeX metrics, outline lowering, and immediate deformation."""

import shutil
from pathlib import Path as FilePath

import pytest

from pdl.author.entity.base import Entity
from pdl.author.geometry.path import Path
from pdl.author.geometry.point import Point
from pdl.author.geometry.tex import TeX
from pdl.author.util.tex import TeXConfig

pytestmark = pytest.mark.skipif(
    not shutil.which("xelatex") or not shutil.which("dvisvgm"), reason="XeLaTeX/dvisvgm unavailable"
)


def test_tex_baseline_and_stretch_use_actual_engine_output(tmp_path: FilePath) -> None:
    geometry = TeX(r"$x^2+1$", position=(3, 5), config=TeXConfig(cache_dir=tmp_path))
    assert geometry.layout_bounds.width > 0
    assert geometry.layout_bounds.bottom <= 5 < geometry.layout_bounds.top
    entity = Entity(geometry)
    entity.scale(2, 1)
    assert isinstance(entity.geometry, Path)
    assert entity.geometry.commands
    assert entity.reference == Point(3, 5)
    # Further edits operate only on the resulting path, without TeX compilation.
    entity.translate(10, 0)
    assert isinstance(entity.geometry, Path)
    assert entity.reference == Point(13, 5)


def test_tex_rotation_keeps_native_source_and_consistent_bounds(tmp_path: FilePath) -> None:
    from pdl import Canvas
    from pdl import TeX as DrawTeX

    entity = DrawTeX(r"$x^2+1$", position=(10, 20), config=TeXConfig(cache_dir=tmp_path))
    before = entity.bounds
    entity.rotate(90)
    assert isinstance(entity.geometry, TeX)
    assert entity.bounds.width == pytest.approx(before.height)
    assert entity.bounds.height == pytest.approx(before.width)
    canvas = Canvas(50, 50).add(entity)
    assert r"$x^2+1$" in canvas.render("tikz")
    assert "<svg" in canvas.render()
