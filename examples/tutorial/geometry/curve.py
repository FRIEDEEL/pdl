# tutorial-start
from pdl import Canvas, Color, Entity, PathGeometry, Style, circle, line

curve = PathGeometry().move_to((10, 10)).cubic_to((10, 35), (45, 35), (45, 10))
blue = Style(stroke=Color(0.15, 0.35, 0.75), line_width=0.6)
guide = Style(stroke=Color(0.65, 0.65, 0.65), line_width=0.2)

canvas = Canvas(55, 45)
canvas.draw(line((10, 10), (10, 35)), guide)
canvas.draw(line((45, 10), (45, 35)), guide)
canvas.draw(Entity(curve), blue)
canvas.draw(circle((10, 35), radius=0.7), guide)
canvas.draw(circle((45, 35), radius=0.7), guide)

# tutorial-end

if __name__ == "__main__":
    from pathlib import Path as FilePath

    output = FilePath(__file__).resolve().parents[2] / "output" / "tutorial" / "geometry"
    output.mkdir(parents=True, exist_ok=True)
    canvas.save(output / "curve.svg")
