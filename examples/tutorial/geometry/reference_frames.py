# tutorial-start
from pdl import Canvas, Color, Frame, Gather, Style, frame_axes, rectangle, text

canvas = Canvas(110, 50)
ghost = Style(stroke=Color(0.75, 0.75, 0.75), line_width=0.25)
blue = Style(fill=Color(0.7, 0.85, 1), line_width=0.4)
for x, together in ((25, False), (80, True)):
    box = rectangle((x - 10, 15), 20, 10)
    reference = Frame((x, 20))
    axes = frame_axes(reference, length=14)
    canvas.draw(box, ghost)
    canvas.add(frame_axes(reference, length=14, x_style=ghost, y_style=ghost, origin_style=ghost))
    if together:
        Gather(box, axes).rotate(30, origin=axes.origin)
    else:
        box.rotate(30, origin=axes.origin)
    canvas.draw(box, blue)
    canvas.add(axes)
    label = "Object + explicit axes" if together else "Object only"
    canvas.add(text(label, position=(x - 20, 5), size=9))

# tutorial-end

if __name__ == "__main__":
    from pathlib import Path as FilePath

    output = FilePath(__file__).resolve().parents[2] / "output" / "tutorial" / "geometry"
    output.mkdir(parents=True, exist_ok=True)
    canvas.save(output / "reference_frames.svg")
    canvas.save(output / "reference_frames.tex", backend="tikz", tikz_mode="tex")
