# tutorial-start
from pdl import Canvas, Circle, Color, CoordinateSystem, Line, Style, Text, Transform

local = CoordinateSystem(transform=Transform.translate(25, 15) @ Transform.rotate(30))
circle = Circle((10, 0), radius=3).in_space(local)
blue = Style(stroke=Color(0.15, 0.35, 0.75), line_width=0.4)
gray = Style(stroke=Color(0.7, 0.7, 0.7), line_width=0.2)

canvas = Canvas(65, 45)
canvas.draw(Line((0, 0), (60, 0)), gray)
canvas.draw(Line((0, 0), (0, 40)), gray)
canvas.draw(Line((0, 0), (25, 0)).in_space(local), blue)
canvas.draw(Line((0, 0), (0, 20)).in_space(local), blue)
canvas.draw(circle, blue)
canvas.draw(Text("local x", position=(48, 25), size=9))
canvas.draw(Text("local y", position=(10, 34), size=9))
canvas.draw(Text("(25, 15)", position=(25, 10), size=9))

# tutorial-end

if __name__ == "__main__":
    from pathlib import Path as FilePath

    output = FilePath(__file__).resolve().parents[2] / "output" / "tutorial" / "geometry"
    output.mkdir(parents=True, exist_ok=True)
    canvas.save(output / "local_coordinates.svg")
