# tutorial-start
from pdl import Canvas, Color, Node, Style, TeX, TeXConfig

config = TeXConfig(packages=("amsmath",), preamble=(r"\newcommand{\energy}{E}",))
formula = TeX(r"$\energy = \frac{1}{2}mv^2$", size=18, config=config)
node = Node(formula, position=(35, 20), style=Style(fill=Color(0.9, 0.95, 1), line_width=0.4))

canvas = Canvas(70, 40)
canvas.draw(node)

# tutorial-end

if __name__ == "__main__":
    from pathlib import Path as FilePath

    output = FilePath(__file__).resolve().parents[2] / "output" / "tutorial" / "advanced"
    output.mkdir(parents=True, exist_ok=True)
    canvas.save(output / "tex_pipeline.svg")
    canvas.save(output / "tex_pipeline.tex", backend="tikz", tikz_mode="pdf")
