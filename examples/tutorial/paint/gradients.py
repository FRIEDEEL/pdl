# tutorial-start
from pdl import (
    Canvas,
    Circle,
    Color,
    ColorStop,
    LinearGradient,
    RadialGradient,
    Rectangle,
    Style,
)

stops = (
    ColorStop(0, Color(0.1, 0.3, 0.8)),
    ColorStop(0.4, Color(0.9, 0.95, 1)),
    ColorStop(1, Color(0.95, 0.4, 0.15)),
)
linear = LinearGradient(stops)
diagonal = LinearGradient(stops, start=(0, 0), end=(1, 1))
radial = RadialGradient(stops)
bar = Rectangle((5, 8), 35, 18).set_style(Style(fill=linear, line_width=0.3))
square = Rectangle((48, 8), 20, 20).set_style(Style(fill=diagonal, line_width=0.3))
disc = Circle((88, 18), 11).set_style(Style(fill=radial, line_width=0.3))

canvas = Canvas(105, 65)
canvas.draw(bar)
canvas.draw(square)
canvas.draw(disc)
bar.rotate(15, center=(22, 17)).translate(0, 30)
canvas.draw(bar)

# tutorial-end

if __name__ == "__main__":
    from pathlib import Path as FilePath

    output = FilePath(__file__).resolve().parents[2] / "output" / "tutorial" / "paint"
    output.mkdir(parents=True, exist_ok=True)
    canvas.save(output / "gradients.svg")
