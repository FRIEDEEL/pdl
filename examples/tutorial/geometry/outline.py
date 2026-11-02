# tutorial-start
from pdl import Canvas, Color, Entity, Style
from pdl.author.geometry import Path as PathGeometry

outline = PathGeometry().move_to((10, 10)).line_to((40, 10)).line_to((30, 30)).close()

canvas = Canvas(55, 40)
canvas.draw(Entity(outline), Style(fill=Color(0.75, 0.85, 1), line_width=0.5))

# tutorial-end

if __name__ == "__main__":
    from pathlib import Path as FilePath

    output = FilePath(__file__).resolve().parents[2] / "output" / "tutorial" / "geometry"
    output.mkdir(parents=True, exist_ok=True)
    canvas.save(output / "outline.svg")
