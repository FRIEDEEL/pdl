# tutorial-start
from pdl import Canvas, Color, Style, rectangle

blue = rectangle((8, 8), 28, 25).set_style(Style(fill=Color(0.4, 0.7, 1)))
gold = rectangle((20, 15), 28, 25).set_style(Style(fill=Color(1, 0.8, 0.3)))
red = rectangle((32, 22), 28, 25).set_style(Style(fill=Color(1, 0.5, 0.45)))
canvas = Canvas(75, 60)
background = canvas.layers[0]
foreground = canvas.layers[1]
middle = canvas.layers.insert_below(foreground, name="middle")
blue.set_layer(background)
red.set_layer(foreground)
middle.add(gold)

canvas.draw(red)
canvas.draw(gold)
canvas.draw(blue)

# tutorial-end

if __name__ == "__main__":
    from pathlib import Path as FilePath

    output = FilePath(__file__).resolve().parents[2] / "output" / "tutorial" / "layout"
    output.mkdir(parents=True, exist_ok=True)
    canvas.save(output / "layers.svg")
