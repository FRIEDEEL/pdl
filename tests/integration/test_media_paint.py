"""Compile actual image and gradient resources with the installed TeX toolchain."""

import shutil
from pathlib import Path

import pytest

from pdl import (
    Canvas,
    Color,
    ColorStop,
    LinearGradient,
    RadialGradient,
    Shear,
    Style,
    circle,
    image,
    rectangle,
)


def test_compile_images_and_gradients_after_moving_export(tmp_path: Path) -> None:
    if shutil.which("xelatex") is None:
        pytest.skip("xelatex is not installed")
    asset = Path(__file__).parents[2] / "examples/tutorial/media/quadrants.png"
    stops = (
        ColorStop(0, Color(1, 0, 0)),
        ColorStop(0.3, Color(1, 1, 1)),
        ColorStop(1, Color(0, 0, 1)),
    )
    canvas = Canvas(100, 70)
    canvas.draw(rectangle((5, 5), 40, 20), Style(fill=LinearGradient(stops, (0, 0), (1, 1))))
    canvas.draw(circle((70, 20), 15), Style(fill=RadialGradient(stops)))
    canvas.draw(image(asset, 40, 20, (20, 40), fit="cover").apply_transform(Shear(0.2)))
    original = tmp_path / "original"
    original.mkdir()
    canvas.save(original / "drawing.tex", backend="tikz", tikz_mode="tex")
    moved = tmp_path / "moved"
    original.rename(moved)
    from pdl.backends.tikz.compiler import compile_pdf

    pdf = compile_pdf(moved / "drawing.tex", mode="pdf")
    assert pdf is not None and pdf.read_bytes().startswith(b"%PDF")
