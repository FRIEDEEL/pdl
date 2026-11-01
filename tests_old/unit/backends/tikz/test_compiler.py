"""Optional tool discovery and source-only saving behavior."""

from pathlib import Path

import pytest

from pdl import Canvas


def test_missing_engine_preserves_source(tmp_path: Path) -> None:
    source = tmp_path / "drawing.tex"
    canvas = Canvas(10, 10, backend="tikz")
    canvas.save(source, engine="pdl-nonexistent-latex")
    assert "tikzpicture" in source.read_text()
    assert list(tmp_path.iterdir()) == [source]
    with pytest.raises(FileNotFoundError, match="unavailable"):
        canvas.save(source, tikz_mode="pdf", engine="pdl-nonexistent-latex")


def test_source_only_mode_does_not_compile(tmp_path: Path) -> None:
    canvas = Canvas(10, 10)
    canvas.save(tmp_path / "drawing.tex", backend="tikz", tikz_mode="tex")
    assert len(list(tmp_path.iterdir())) == 1


def test_invalid_mode_is_rejected_before_writing(tmp_path: Path) -> None:
    from pdl.backends.tikz.compiler import compile_pdf

    with pytest.raises(ValueError, match="mode"):
        compile_pdf(tmp_path / "drawing.tex", mode="invalid")  # type: ignore[arg-type]
    assert not list(tmp_path.iterdir())
