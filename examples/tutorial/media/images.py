from pathlib import Path as FilePath

from pdl import Canvas, Color, Style, image, rectangle

image_file = FilePath(__file__).with_name("quadrants.png")


# tutorial-start
contained = image(image_file, 24, 24, (5, 8), fit="contain")
covered = image(image_file, 24, 24, (35, 8), fit="cover")
stretched = image(image_file, 24, 24, (65, 8), fit="stretch")
frames = tuple(rectangle((x, 8), 24, 24) for x in (5, 35, 65))

canvas = Canvas(95, 40)
for image_entity in (contained, covered, stretched):
    canvas.draw(image_entity)
for frame in frames:
    canvas.draw(frame, Style(stroke=Color(0.2, 0.2, 0.2), line_width=0.3))

# tutorial-end

if __name__ == "__main__":
    from pathlib import Path as FilePath

    output = FilePath(__file__).resolve().parents[2] / "output" / "tutorial" / "media"
    output.mkdir(parents=True, exist_ok=True)
    canvas.save(output / "images.svg")
