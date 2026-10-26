"""Backend semantics, fallback and real TikZ compilation."""

import shutil
import subprocess
from pathlib import Path as FilePath

import pytest

from pdl import Arc, Canvas, Color, Path, Style


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
