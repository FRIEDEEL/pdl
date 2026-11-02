"""Backend semantics, fallback and real TikZ compilation."""

import shutil
from pathlib import Path as FilePath

import pytest

from pdl import Arc, Canvas, Color, Entity, Style
from pdl import PathGeometry as Path


def test_tikz_compiles(tmp_path: FilePath) -> None:
    executable = shutil.which("pdflatex")
    if executable is None:
        pytest.skip("pdflatex is not installed")
    canvas = Canvas(40, 30)
    canvas.draw(
        Entity(Path().move_to((1, 1)).quadratic_to((10, 25), (20, 1)).close()),
        Style(fill=Color(0.2, 0.4, 0.8)),
    )
    canvas.draw(Arc((20, 15), 8, 5, 0, 270, rotation=20))
    source = tmp_path / "drawing.tex"
    canvas.save(source, backend="tikz", tikz_mode="pdf", engine="pdflatex")
    assert (tmp_path / "drawing.pdf").stat().st_size > 0
    assert {path.suffix for path in tmp_path.iterdir()} == {".tex", ".pdf"}


def test_tikz_keeps_intermediates_when_requested(tmp_path: FilePath) -> None:
    if shutil.which("xelatex") is None:
        pytest.skip("xelatex is not installed")
    canvas = Canvas(10, 10)
    canvas.save(tmp_path / "drawing.tex", backend="tikz", tikz_mode="pdf", keep_intermediates=True)
    assert (tmp_path / "drawing.pdf").stat().st_size > 0
    assert (tmp_path / "drawing.aux").exists()
    assert (tmp_path / "drawing.log").exists()


def test_compilation_failure_keeps_source_without_auxiliary_files(tmp_path: FilePath) -> None:
    from pdl.backends.tikz.compiler import compile_pdf

    if shutil.which("xelatex") is None:
        pytest.skip("xelatex is not installed")
    source = tmp_path / "broken.tex"
    source.write_text(r"\documentclass{article}\begin{document}\undefinedPDL\end{document}")
    with pytest.raises(RuntimeError, match="compilation failed"):
        compile_pdf(source, mode="pdf")
    assert list(tmp_path.iterdir()) == [source]
