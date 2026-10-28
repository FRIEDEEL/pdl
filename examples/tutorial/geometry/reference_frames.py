# tutorial-start
from pdl import Canvas, Color, Frame, Gather, Rectangle, Style, Text

canvas = Canvas(110, 50)
ghost = Style(stroke=Color(0.75, 0.75, 0.75), line_width=0.25)
blue = Style(fill=Color(0.7, 0.85, 1), line_width=0.4)

for x, together in ((25, False), (80, True)):
    box = Rectangle((x - 10, 15), 20, 10)
    box.frame = Frame((x, 20))
    canvas.draw(box, ghost)
    canvas.draw(box.frame.visualize(axis_length=14, x_style=ghost, y_style=ghost))

    if together:
        Gather(box, box.frame).rotate(30, about=box.frame.origin)
    else:
        box.rotate(30, about=box.frame.origin)

    canvas.draw(box, blue)
    canvas.draw(box.frame.visualize(axis_length=14))
    label = "Object + frame" if together else "Object only"
    canvas.draw(Text(label, position=(x - 15, 5), size=10))
# tutorial-end

if __name__ == "__main__":
    from pathlib import Path as FilePath

    output = FilePath(__file__).resolve().parents[2] / "output" / "tutorial" / "geometry"
    output.mkdir(parents=True, exist_ok=True)
    canvas.save(output / "reference_frames.svg")
    canvas.save(output / "reference_frames.tex", backend="tikz", tikz_mode="tex")
