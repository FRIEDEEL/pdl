"""Renderer-level font policy and native text regressions."""

from pathlib import Path as FilePath

import pytest

from pdl import Canvas, Font, RendererConfig, TeX, TeXConfig, Text
from pdl.geometry.primitives import Path


def test_native_text_does_not_generate_outlines(
    font: Font, monkeypatch: pytest.MonkeyPatch
) -> None:
    def unexpected(file: str, index: int, gid: int) -> Path:
        raise AssertionError("Native text must not request a glyph outline.")

    monkeypatch.setattr("pdl.typography.plain.glyph_path", unexpected)
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
    with pytest.raises(ValueError, match="Specify"):
        canvas.render()
