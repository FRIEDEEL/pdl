"""Real TeX measurement, baseline preservation, cache and native export."""

import shutil
import subprocess
from pathlib import Path as FilePath
from xml.etree import ElementTree as ET

import pytest

from pdl import Canvas
from pdl.geometry.transforms import Transform
from pdl.scene.composition import Drawing, Group, bounds
from pdl.typography.tex import TeX, TeXConfig


@pytest.fixture
def config(tmp_path: FilePath) -> TeXConfig:
    if not shutil.which("xelatex") or not shutil.which("dvisvgm"):
        pytest.skip("XeLaTeX and dvisvgm are required for TeX integration tests.")
    return TeXConfig(
        cache_dir=tmp_path / "cache",
        packages=("amsmath", "amssymb"),
        preamble=(r"\newcommand{\RR}{\mathbb{R}}",),
    )


def test_measure_baseline_and_cached_svg(config: TeXConfig) -> None:
    tex = TeX(r"$\frac{x_i}{y^2}+\RR$", position=(10, 20), config=config)
    layout = tex.layout
    assert layout.width > 0 and layout.height > 0 and layout.depth > 0
    box = bounds(tex)
    assert box.left == pytest.approx(10)
    assert box.bottom == pytest.approx(20 - layout.depth)
    assert tex.layout == layout
    assert tex.to_path().commands
    assert len(list(FilePath(config.cache_dir or "").glob("*.json"))) == 1


def test_two_fragments_have_unique_svg_ids(config: TeXConfig) -> None:
    tex = TeX(r"$x_i$", config=config)
    canvas = Canvas(40, 30)
    canvas.draw(tex)
    canvas.draw(Group((Drawing(tex),), Transform.translate(10, 10)))
    root = ET.fromstring(canvas.render())
    ids = [el.attrib["id"] for el in root.iter() if "id" in el.attrib]
    assert len(ids) == len(set(ids))
    assert any("tex0-" in item for item in ids)
    assert any("tex1-" in item for item in ids)


def test_native_tex_and_embedding(config: TeXConfig, tmp_path: FilePath) -> None:
    canvas = Canvas(40, 30)
    tex = TeX(r"$\frac{x_i}{y^2}+\RR$", position=(3, 10), config=config)
    canvas.draw(Group((Drawing(tex),), Transform.translate(1, 2) @ Transform.rotate(15)))
    fragment = canvas.render("tikz", standalone=False)
    assert tex.source in fragment
    assert r"\documentclass" not in fragment
    assert r"\usepackage{amssymb}" in canvas.latex_preamble()
    source = (
        r"\documentclass{article}"
        + "\n"
        + canvas.latex_preamble()
        + r"\begin{document}"
        + fragment
        + r"\end{document}"
    )
    file = tmp_path / "embedding.tex"
    file.write_text(source)
    result = subprocess.run(
        ["xelatex", "-no-shell-escape", "-interaction=nonstopmode", "-halt-on-error", file.name],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    assert result.returncode == 0, result.stdout[-6000:]
    assert (tmp_path / "embedding.pdf").is_file()


def test_incompatible_configs_are_not_silently_merged(config: TeXConfig) -> None:
    canvas = Canvas(40, 30)
    canvas.draw(TeX("A", config=config))
    canvas.draw(TeX("B"))
    with pytest.raises(ValueError, match="shared TeXConfig"):
        canvas.render("tikz")


def test_compilation_failure_has_diagnostic(config: TeXConfig) -> None:
    with pytest.raises(RuntimeError, match="Undefined control sequence"):
        TeX(r"\pdlUndefinedCommand", config=config).layout


def test_cache_tracks_declared_dependency_contents(config: TeXConfig, tmp_path: FilePath) -> None:
    from dataclasses import replace

    dependency = tmp_path / "dependency.txt"
    dependency.write_text("version one")
    configured = replace(config, dependencies=(dependency,))
    tex = TeX("A", config=configured)
    first = tex.layout
    dependency.write_text("version two")
    assert tex.layout == first
    assert len(list(FilePath(config.cache_dir or "").glob("*.json"))) == 2


def test_empty_tex_has_zero_layout(config: TeXConfig) -> None:
    tex = TeX("", config=config)
    assert tex.layout.width == tex.layout.height == tex.layout.depth == 0
    canvas = Canvas(10, 10)
    canvas.draw(tex)
    ET.fromstring(canvas.render())


def test_singular_tex_placement_is_invisible() -> None:
    canvas = Canvas(10, 10)
    canvas.draw(Group((Drawing(TeX("A")),), Transform.scale(0)))
    assert r"\node" not in canvas.render("tikz")
    assert "tex0-" not in canvas.render()
