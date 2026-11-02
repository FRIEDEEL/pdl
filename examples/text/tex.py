"""Native TeX, packages/macros and the same output embedded into SVG."""

from examples._shared import LABEL, export, output_base
from pdl import Canvas, RendererConfig, TeX, TeXConfig, Text
from pdl.extensions.diagram.debug import debug_overlay

CONFIG = TeXConfig(
    packages=("amsmath", "amssymb"),
    preamble=("\\usepackage[fontset=fandol]{ctex}", "\\newcommand{\\vect}[1]{\\mathbf{#1}}"),
)
SHOW_DEBUG = True


def example() -> Canvas:
    canvas = Canvas(190, 125, renderer=RendererConfig(fonts=("sans-serif",), tex=CONFIG))
    title = Text("TeX / native source and vector fragments", size=16, position=(8, 112))
    formula = TeX(
        "$p < 10^{-6}\\,\\mathrm{mbar},\\quad \\alpha_i=\\frac{x_i}{y^2}$",
        (12, 91),
        size=16,
    )
    matrix = TeX(
        "$\\vect{v}=\\begin{pmatrix}x\\\\y\\\\z\\end{pmatrix}\\in\\mathbb{R}^3$",
        (12, 58),
        size=15,
    )
    mixed = TeX("样品温度：$T=300\\,\\mathrm{K}$；流量 $Q=\\dot{V}$", (12, 27), size=14)
    note = Text(
        "Original TeX survives in .tex; SVG contains the same measured vector content.",
        size=9,
        position=(8, 7),
    )
    canvas.draw(title, LABEL)
    with canvas.typography():
        for tex in (formula, matrix, mixed):
            canvas.draw(tex)
            if SHOW_DEBUG:
                canvas.draw(debug_overlay(tex))
    canvas.draw(note, LABEL)
    return canvas


def export_embedding(canvas: Canvas) -> None:
    """Show a TikZ fragment inside an ordinary article document."""
    destination = output_base(__file__).parent
    fragment = canvas.render("tikz", standalone=False)
    (destination / "tex-fragment.tex").write_text(fragment, encoding="utf-8")
    (destination / "tex-preamble.tex").write_text(canvas.latex_preamble(), encoding="utf-8")
    document = (
        "\\documentclass{article}"
        + "\n"
        + canvas.latex_preamble()
        + "\\usepackage[margin=10mm]{geometry}"
        + "\n"
        + "\\begin{document}"
        + "\n"
        + "\\section*{Native pdl figure}"
        + "\n"
        + fragment
        + "\\end{document}"
        + "\n"
    )
    (destination / "tex-embedded.tex").write_text(document, encoding="utf-8")


if __name__ == "__main__":
    canvas = example()
    export(canvas, __file__)
    export_embedding(canvas)
