# tutorial-start
from pdl import Canvas, Color, Style, circle, rectangle

rectangle_entity = rectangle((10, 10), width=30, height=20)
circle_entity = circle((65, 20), radius=10)

canvas = Canvas(60, 40, mode="clip", padding=4)
canvas.draw(rectangle_entity, Style(fill=Color(1, 0.7, 0.35), line_width=0.5))
canvas.draw(circle_entity, Style(fill=Color(0.6, 0.8, 1), line_width=0.5))

# tutorial-end

if __name__ == "__main__":
    from pathlib import Path as FilePath

    output = FilePath(__file__).resolve().parents[2] / "output" / "tutorial" / "advanced"
    output.mkdir(parents=True, exist_ok=True)
    canvas.save(output / "viewport_clip.svg")
