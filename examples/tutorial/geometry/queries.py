# tutorial-start
from pdl import Canvas, Color, Style, rectangle
from pdl.author.geometry import WORLD

box = rectangle((-10, -5), width=20, height=10).move_to((30, 20), anchor="center")
box.rotate(30, origin=(30, 20))

canvas = Canvas(65, 45)
canvas.draw(box, Style(fill=Color(0.6, 0.8, 1), line_width=0.5))
bounds = canvas.query().bounds(box, in_space=WORLD)
frame = rectangle((bounds.left, bounds.bottom), bounds.width, bounds.height)
canvas.draw(frame, Style(stroke=Color(0.85, 0.2, 0.15), line_width=0.25))

# Numerical results can be used to place new objects.
center = bounds.anchor("center")
print(f"Center: ({center.x:.1f}, {center.y:.1f}) mm")

# tutorial-end

if __name__ == "__main__":
    from pathlib import Path as FilePath

    output = FilePath(__file__).resolve().parents[2] / "output" / "tutorial" / "geometry"
    output.mkdir(parents=True, exist_ok=True)
    canvas.save(output / "queries.svg")
