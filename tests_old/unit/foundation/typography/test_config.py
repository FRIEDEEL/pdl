"""Renderer-level font policy and native text regressions."""

from pathlib import Path as FilePath

import pytest

from pdl import Canvas, Font, Line, RendererConfig, TeX, TeXConfig, Text
from pdl.author.shapes import Path


def test_native_text_does_not_generate_outlines(
    font: Font, monkeypatch: pytest.MonkeyPatch
) -> None:
    def unexpected(file: str, index: int, gid: int) -> Path:
        raise AssertionError("Native text must not request a glyph outline.")

    monkeypatch.setattr("pdl.foundation.typography.shaping.glyph_path", unexpected)
    canvas = Canvas(50, 30, renderer=RendererConfig(fonts=(font,)))
    canvas.draw(Text("Editable label", position=(2, 10)))
    svg = canvas.render()
    tikz = canvas.render("tikz")
    assert "Editable label</text>" in svg and "<path" not in svg
    assert "Editable label" in tikz and "controls" not in tikz
    assert r"\newfontfamily" in tikz and r"\node" in tikz


def test_renderer_supplies_shared_tex_environment(tmp_path: FilePath) -> None:
    import shutil

    if not shutil.which("xelatex") or not shutil.which("dvisvgm"):
        pytest.skip("XeLaTeX integration tools unavailable.")
    config = TeXConfig(cache_dir=tmp_path, preamble=(r"\newcommand{\PDLlabel}{Native}",))
    canvas = Canvas(50, 30, renderer=RendererConfig(tex=config))
    canvas.draw(TeX(r"\PDLlabel", position=(2, 10)))
    assert r"\newcommand{\PDLlabel}" in canvas.latex_preamble()
    assert "<svg" in canvas.render()
    assert r"\PDLlabel" in canvas.render("tikz")


def test_font_discovery_at_render_start(font: Font) -> None:
    canvas = Canvas(50, 30)
    canvas.draw(Text("Discovered label"))
    rendered = canvas.render(renderer=RendererConfig(fonts=(str(font.file),)))
    assert "Discovered label</text>" in rendered
    assert "Discovered label</text>" in canvas.render()


def test_unconfigured_first_render_uses_default_font(
    font: Font, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("pdl.foundation.typography.config.default_fonts", lambda: (font,))
    canvas = Canvas(50, 30)
    canvas.draw(Text("First render", position=(2, 10)))
    assert "First render</text>" in canvas.render()
    assert "First render" in canvas.render("tikz")


def test_geometry_and_explicit_text_do_not_require_default_discovery(
    font: Font, monkeypatch: pytest.MonkeyPatch
) -> None:
    def missing() -> tuple[Font, ...]:
        raise FileNotFoundError("No default font")

    monkeypatch.setattr("pdl.foundation.typography.config.default_fonts", missing)
    canvas = Canvas(50, 30)
    canvas.draw(Line((0, 0), (10, 10)))
    canvas.draw(Text("Explicit", font))
    assert "<text" in canvas.render()
    assert "Explicit" in canvas.render("tikz")
    with pytest.raises(FileNotFoundError, match="default font"):
        canvas.draw(Text("Needs default"))
