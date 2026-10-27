# tutorial-start
from pdl import Canvas, TeX

formula = TeX(r"$E = mc^2$", position=(10, 12), size=20)

canvas = Canvas(65, 30)
canvas.draw(formula)

# tutorial-end

if __name__ == "__main__":
    from pathlib import Path as FilePath

    output = FilePath(__file__).resolve().parents[2] / "output" / "tutorial" / "text"
    output.mkdir(parents=True, exist_ok=True)
    canvas.save(output / "formula.svg")
    canvas.save(output / "formula.tex", backend="tikz", tikz_mode="pdf")
