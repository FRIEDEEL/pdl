# tutorial-start
from pdl import Canvas, Entity, Node, Text

label = Entity(Node(Text("Snapshot"))).move_to((25, 15))

canvas = Canvas(80, 45)
canvas.draw(label)
frozen = canvas.resolve(label)
label.translate(30, 15)
canvas.draw(label)

# This canvas receives the fixed geometry at its already resolved position.
copy = Canvas(80, 45)
copy.draw(frozen)

# tutorial-end

if __name__ == "__main__":
    from pathlib import Path as FilePath

    output = FilePath(__file__).resolve().parents[2] / "output" / "tutorial" / "advanced"
    output.mkdir(parents=True, exist_ok=True)
    canvas.save(output / "resolved.svg")
    copy.save(output / "resolved-copy.svg")
