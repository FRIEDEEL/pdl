# tutorial-start
from pdl import Canvas, Color, Style, line, text

small = text("Hello world", position=(10, 25), size=12)
large = text("Hello world", position=(10, 12), size=20)
blue = Style(stroke=None, fill=Color(0.15, 0.35, 0.75))

canvas = Canvas(75, 40)
canvas.draw(small)
canvas.draw(large, blue)

# Optional guides show the baseline reference for each label.
guide = Style(stroke=Color(0.7, 0.7, 0.7), line_width=0.15)
canvas.draw(line((5, 25), (65, 25)), guide)
canvas.draw(line((5, 12), (65, 12)), guide)

# tutorial-end

if __name__ == "__main__":
    from pathlib import Path as FilePath

    output = FilePath(__file__).resolve().parents[2] / "output" / "tutorial" / "text"
    output.mkdir(parents=True, exist_ok=True)
    canvas.save(output / "labels.svg")
