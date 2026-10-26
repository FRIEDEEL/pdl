"""Text measurements, shaping and outline export behavior."""

import pytest

from pdl import Canvas, Point
from pdl.scene import bounds
from pdl.text import Font, Text


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


def test_literal_special_characters_and_outlines(font: Font) -> None:
    text = Text("A&B $ 50% café", font, position=Point(5, 6))
    canvas = Canvas(100, 30)
    canvas.draw(text)
    assert 'fill="rgb(0%,0%,0%)"' in canvas.render()
    assert "controls" in canvas.render("tikz")
    assert text.text == "A&B $ 50% café"


def test_missing_glyph_is_explicit(font: Font) -> None:
    with pytest.raises(ValueError, match="lacks glyphs"):
        Text("\U0010ffff", font).to_path()


def test_layout_snapshot_is_independent(font: Font) -> None:
    text = Text("A", font)
    path = text.to_path()
    original = len(path.commands)
    path.line_to((100, 100))
    assert len(text.to_path().commands) == original
