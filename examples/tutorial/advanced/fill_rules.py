# tutorial-start
from pdl import Canvas, Color, PathGeometry, Style
from pdl.author.entity.factories import as_entity
from pdl.author.geometry.shapes import Circle as CircleGeometry

rings = (
    PathGeometry()
    .extend(CircleGeometry((15, 15), radius=10))
    .extend(CircleGeometry((15, 15), radius=5))
)
blue = Color(0.6, 0.8, 1)

canvas = Canvas(65, 30)
canvas.draw(as_entity(rings), Style(fill=blue, line_width=0.4, fill_rule="nonzero"))
canvas.draw(
    as_entity(rings).translate(35, 0),
    Style(fill=blue, line_width=0.4, fill_rule="evenodd"),
)

# tutorial-end

if __name__ == "__main__":
    from pathlib import Path as FilePath

    output = FilePath(__file__).resolve().parents[2] / "output" / "tutorial" / "advanced"
    output.mkdir(parents=True, exist_ok=True)
    canvas.save(output / "fill_rules.svg")
