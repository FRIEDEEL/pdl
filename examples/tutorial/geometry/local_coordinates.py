# tutorial-start
from pdl import Canvas, Color, Style, circle, line, text
from pdl.author.geometry import Frame
from pdl.author.transform import Rotation, Translation

local = Frame().child(Translation(25, 15) @ Rotation(30))
circle_entity = circle(local.point((10, 0)), radius=3)
blue = Style(stroke=Color(0.15, 0.35, 0.75), line_width=0.4)
gray = Style(stroke=Color(0.7, 0.7, 0.7), line_width=0.2)
canvas = Canvas(65, 45)
canvas.draw(line((0, 0), (60, 0)), gray)
canvas.draw(line((0, 0), (0, 40)), gray)
canvas.draw(line(local.point((0, 0)), local.point((25, 0))), blue)
canvas.draw(line(local.point((0, 0)), local.point((0, 20))), blue)
canvas.draw(circle_entity, blue)
canvas.add(
    text("local x", position=(48, 25), size=9),
    text("local y", position=(10, 34), size=9),
    text("(25,15)", position=(25, 10), size=9),
)

# tutorial-end

if __name__ == "__main__":
    from pathlib import Path as FilePath

    output = FilePath(__file__).resolve().parents[2] / "output" / "tutorial" / "geometry"
    output.mkdir(parents=True, exist_ok=True)
    canvas.save(output / "local_coordinates.svg")
