# tutorial-start
from pdl import Canvas, Color, Style, circle, text

ghost = Style(stroke=Color(0.7, 0.7, 0.7), line_width=0.3)
blue = Style(stroke=Color(0.15, 0.35, 0.75), line_width=0.5)
canvas = Canvas(110, 55)
stretched = circle((25, 32), 6, style=blue)
canvas.draw(stretched, ghost)
stretched.scale(2, 0.75)
canvas.add(stretched)
scaled = circle((80, 32), 4.5, style=blue)
canvas.draw(scaled, ghost)
scaled.rescale(2, include_linewidth=True)
canvas.add(scaled)
canvas.add(text("stretch / fixed line", position=(25, 10), align="center", size=10))
canvas.add(text("rescale / include line", position=(80, 10), align="center", size=10))

# tutorial-end

if __name__ == "__main__":
    from pathlib import Path as FilePath

    output = FilePath(__file__).resolve().parents[2] / "output" / "tutorial" / "geometry"
    output.mkdir(parents=True, exist_ok=True)
    canvas.save(output / "scaling.svg")
