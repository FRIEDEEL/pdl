"""Text measurements, shaping and outline export behavior."""

import pytest

from pdl.author.geometry.path import Path
from pdl.author.geometry.point import Point
from pdl.author.geometry.queries import bounds_of as bounds
from pdl.author.geometry.text import Text
from pdl.author.style.font import Font


def test_whitespace_has_advance_but_no_ink(font: Font) -> None:
    text = Text("   ", font)
    assert text.layout.box.width > 0
    assert not text.to_path().commands
    assert bounds(text).width > 0


def test_multiline_alignment_and_baseline(font: Font) -> None:
    text = Text("AV\nshort", font, position=(20, 30), align="center")
    assert text.layout_bounds.anchor().x == pytest.approx(20)
    assert text.layout_bounds.bottom < 30 < text.layout_bounds.top
    assert len(text.layout.advances) == 2
    assert Text("AV", font).layout.advances[0] < (
        Text("A", font).layout.advances[0] + Text("V", font).layout.advances[0]
    )


def test_missing_glyph_is_explicit(font: Font) -> None:
    with pytest.raises(ValueError, match="lack glyphs"):
        Text("\U0010ffff", font).to_path()


def test_layout_snapshot_is_independent(font: Font) -> None:
    text = Text("A", font)
    path = text.to_path()
    original = len(path.commands)
    path.line_to((100, 100))
    assert len(text.to_path().commands) == original


def test_japanese_first_chinese_fallback() -> None:
    import shutil
    import subprocess
    from pathlib import Path

    from pdl.author.style.font import FontStack

    executable = shutil.which("kpsewhich")
    if executable is None:
        pytest.skip("TeX example fonts unavailable.")
    paths: list[str] = []
    for name in ("HaranoAjiGothic-Regular.otf", "FandolHei-Regular.otf"):
        result = subprocess.run([executable, name], capture_output=True, text=True, check=False)
        file = result.stdout.strip()
        if not file or not Path(file).is_file():
            pytest.skip("Japanese and Chinese test fonts unavailable.")
        paths.append(file)
    text = Text("真空系统と流量", FontStack(tuple(Font(file) for file in paths)))
    assert text.to_path().commands
    assert text.layout.fonts_used == tuple(paths)
    with pytest.raises(ValueError, match="lack glyphs"):
        Text("真空系统と流量", Font(paths[0])).to_path()


def test_translation_does_not_request_outlines(font: Font, monkeypatch: pytest.MonkeyPatch) -> None:
    from pdl.author.entity.base import Entity

    def unexpected(_self: Text) -> Path:
        raise AssertionError("Translation must not outline or measure text.")

    monkeypatch.setattr(Text, "to_path", unexpected)
    entity = Entity(Text("Native", font, position=(5, 6)))
    entity.translate(2, 3)
    assert isinstance(entity.geometry, Text)
    assert entity.reference == Point(7, 9)


def test_stretch_converts_text_to_path_once(font: Font) -> None:
    from pdl.author.entity.base import Entity
    from pdl.author.geometry.path import Path

    entity = Entity(Text("AB", font, position=(5, 6)))
    entity.scale(2, 1)
    assert isinstance(entity.geometry, Path)
    assert entity.geometry.commands
    assert entity.reference == Point(5, 6)


def test_positive_uniform_scale_retains_native_text(font: Font) -> None:
    from pdl.author.entity.base import Entity

    entity = Entity(Text("Native", font, position=(5, 6), size=12))
    entity.rescale(2)
    assert isinstance(entity.geometry, Text)
    assert entity.geometry.size == 24
    assert entity.reference == Point(5, 6)
