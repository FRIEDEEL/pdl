# tutorial-start
from pdl import Canvas, Circle, Color, Style

original = Circle((15, 12), 5)
other = original.copy().translate(25, 0)
canvas = Canvas(60, 40)
canvas.draw(original, Style(stroke=Color(0.7, 0.7, 0.7), line_width=0.3))
original.translate(0, 15)
canvas.draw(original, Style(fill=Color(0.6, 0.8, 1), line_width=0.4))
canvas.draw(other, Style(fill=Color(1, 0.75, 0.4), line_width=0.4))
# tutorial-end

if __name__ == "__main__":
    from pathlib import Path as FilePath

    output = FilePath(__file__).resolve().parents[2] / "output" / "tutorial" / "geometry"
    output.mkdir(parents=True, exist_ok=True)
    canvas.save(output / "copy_and_capture.svg")
