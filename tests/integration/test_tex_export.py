"""Real native TeX fragments, baseline caches, portable embedding, and nodes."""

import shutil
import subprocess
from dataclasses import replace
from pathlib import Path
from xml.etree import ElementTree as ET

import pytest

from pdl import Canvas, tex, text
from pdl.author.geometry.tex import TeX as TeXGeometry
from pdl.author.style import Font, RendererConfig
from pdl.author.util.tex import TeXConfig
from pdl.extensions.diagram import Connection, Node


@pytest.fixture
def config(tmp_path: Path) -> TeXConfig:
    if not shutil.which("xelatex") or not shutil.which("dvisvgm"):
        pytest.skip("XeLaTeX/dvisvgm unavailable")
    return TeXConfig(
        cache_dir=tmp_path / "cache",
        packages=("amsmath", "amssymb"),
        preamble=(r"\newcommand{\RR}{\mathbb{R}}",),
    )


def test_native_fragments_have_fixed_baselines_and_unique_svg_ids(config: TeXConfig) -> None:
    entity = tex(r"$\frac{x_i}{y^2}+\RR$", position=(10, 20), config=config)
    geometry = entity.geometry
    assert isinstance(geometry, TeXGeometry)
    layout = geometry.layout
    assert layout.width > 0 and layout.height > 0 and layout.depth > 0
    assert entity.bounds.bottom == pytest.approx(20 - layout.depth)
    assert geometry.to_path().commands
    canvas = Canvas(80, 40).add(entity, entity.copy().translate(30, 0))
    root = ET.fromstring(canvas.render())
    ids = [el.attrib["id"] for el in root.iter() if "id" in el.attrib]
    assert len(ids) == len(set(ids))
    assert len(list(Path(config.cache_dir or "").glob("*.json"))) == 1


def test_native_tex_rotates_and_embeds_in_another_document(
    config: TeXConfig, tmp_path: Path
) -> None:
    entity = tex(r"$\frac{x_i}{y^2}+\RR$", position=(3, 10), config=config).rotate(15)
    canvas = Canvas(50, 30).add(entity)
    fragment = canvas.render("tikz", standalone=False)
    assert r"$\frac{x_i}{y^2}+\RR$" in fragment
    assert r"\documentclass" not in fragment
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
    assert file.with_suffix(".pdf").is_file()


def test_shared_tex_environment_is_required(config: TeXConfig) -> None:
    canvas = Canvas(40, 30).add(tex("A", config=config), tex("B"))
    with pytest.raises(ValueError, match="shared TeXConfig"):
        canvas.render("tikz")
    with pytest.raises(RuntimeError, match="Undefined control sequence"):
        TeXGeometry(r"\pdlUndefinedCommand", config=config).layout


def test_cache_tracks_declared_dependency_contents(config: TeXConfig, tmp_path: Path) -> None:
    dependency = tmp_path / "dependency.txt"
    dependency.write_text("one")
    geometry = TeXGeometry("A", config=replace(config, dependencies=(dependency,)))
    first = geometry.layout
    dependency.write_text("two")
    assert geometry.layout == first
    assert len(list(Path(config.cache_dir or "").glob("*.json"))) == 2


def test_empty_and_singular_tex_are_valid(config: TeXConfig) -> None:
    empty = tex("", config=config)
    assert empty.bounds.width == 0
    ET.fromstring(Canvas(10, 10).add(empty).render())
    singular = tex("A", config=config).scale(0)
    canvas = Canvas(10, 10).add(singular)
    assert r"\node" not in canvas.render("tikz")


def test_nodes_compile_using_the_same_text_and_tex_policy(
    config: TeXConfig, font: Font, tmp_path: Path
) -> None:
    first = Node(text("Source", font), position=(20, 20))
    second = Node(
        tex(r"$\frac{x_i}{y^2}+\RR$", config=config), position=first.anchor("east") + (40, 0)
    )
    canvas = Canvas(100, 50, renderer=RendererConfig(fonts=(font,), tex=config))
    canvas.add(Connection(first.anchor("east"), second.anchor("west")), second, first)
    canvas.save(tmp_path / "nodes.tex", backend="tikz", tikz_mode="pdf")
    assert (tmp_path / "nodes.pdf").read_bytes().startswith(b"%PDF")
    ET.fromstring(canvas.render())


def test_tex_ink_query_excludes_layout_whitespace(config: TeXConfig) -> None:
    entity = tex(r"\quad x\quad", position=(5, 10), config=config)
    canvas = Canvas(80, 30)
    layout = canvas.query().bounds(entity)
    ink = canvas.query().ink_bounds(entity)
    assert 0 < ink.width < layout.width


def test_tex_rescale_changes_fixed_mm_geometry_without_retypesetting(config: TeXConfig) -> None:
    entity = tex(r"\rule{10mm}{2mm}", position=(5, 10), config=config)
    before = entity.bounds
    entity.rescale(2)
    assert entity.bounds.width == pytest.approx(before.width * 2, abs=0.001)
    assert entity.bounds.height == pytest.approx(before.height * 2, abs=0.001)
