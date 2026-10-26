"""Backend semantics, fallback and real TikZ compilation."""

import shutil
import subprocess
from pathlib import Path as FilePath
from xml.etree import ElementTree as ET

import pytest

from pdl import Arc, Canvas, Color, Path, Style


def test_open_fill_does_not_close_stroke() -> None:
    canvas = Canvas(10, 10)
    canvas.draw(
        Path().move_to((1, 1)).line_to((8, 1)).line_to((4, 8)),
        Style(fill=Color(1, 0, 0), fill_rule="evenodd"),
    )
    element = ET.fromstring(canvas.render())[0][0]
    assert "Z" not in element.attrib["d"]
    assert element.attrib["fill-rule"] == "evenodd"
    assert "cycle" not in canvas.render("tikz")
    assert "even odd rule" in canvas.render("tikz")


def test_quadratic_is_exactly_elevated_for_tikz() -> None:
    canvas = Canvas(10, 10)
    canvas.draw(Path().move_to((0, 0)).quadratic_to((3, 6), (6, 0)))
    assert "Q 3 6 6 0" in canvas.render()
    assert "controls (2,4) and (4,4) .. (6,0)" in canvas.render("tikz")


def test_native_arc_and_rotated_fallback() -> None:
    canvas = Canvas(30, 30)
    canvas.draw(Arc((10, 10), 4, 2, 0, 360))
    assert canvas.render().count(" A ") == 2
    assert "arc[" in canvas.render("tikz")
    canvas.draw(Arc((10, 10), 4, 2, 0, 90, rotation=30))
    assert "controls" in canvas.render("tikz")


def test_custom_geometry_fallback() -> None:
    class Custom:
        def to_path(self) -> Path:
            return Path().move_to((1, 2)).line_to((3, 4))

    canvas = Canvas(10, 10)
    canvas.draw(Custom())
    assert 'd="M 1 2 L 3 4"' in canvas.render()
    assert "(1,2) -- (3,4)" in canvas.render("tikz")


def test_tikz_compiles(tmp_path: FilePath) -> None:
    executable = shutil.which("pdflatex")
    if executable is None:
        pytest.skip("pdflatex is not installed")
    canvas = Canvas(40, 30)
    canvas.draw(
        Path().move_to((1, 1)).quadratic_to((10, 25), (20, 1)).close(),
        Style(fill=Color(0.2, 0.4, 0.8)),
    )
    canvas.draw(Arc((20, 15), 8, 5, 0, 270, rotation=20))
    source = tmp_path / "drawing.tex"
    canvas.save(source, backend="tikz")
    result = subprocess.run(
        [executable, "-interaction=nonstopmode", "-halt-on-error", source.name],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    assert result.returncode == 0, result.stdout[-6000:]
    assert (tmp_path / "drawing.pdf").stat().st_size > 0
