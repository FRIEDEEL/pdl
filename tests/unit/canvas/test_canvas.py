"""Canvas ordering and output contract."""

from pathlib import Path
from xml.etree import ElementTree as ET

import pytest

from pdl import Canvas, Circle, Color, Rectangle, Style


def test_order_and_native_identity() -> None:
    canvas = Canvas(30, 20)
    circle = Circle((5, 5), 3)
    canvas.draw(circle)
    canvas.draw(Rectangle((0, 0), 2, 2))
    captured = canvas.snapshot(canvas.drawings[0]).geometry
    assert isinstance(captured, Circle)
    assert captured is not circle
    assert captured.radius == 3
    root = ET.fromstring(canvas.render())
    assert root.attrib["width"] == "30mm"
    group = root[0]
    assert [element.tag.rsplit("}", 1)[-1] for element in group] == ["circle", "rect"]
    assert group.attrib["transform"] == "translate(0 20) scale(1 -1)"


def test_save(tmp_path: Path) -> None:
    canvas = Canvas(10, 10)
    filename = tmp_path / "drawing.svg"
    canvas.save(filename, backend="svg")
    assert filename.read_text() == canvas.render("svg")


def test_invalid_canvas_and_color() -> None:
    with pytest.raises(ValueError):
        Canvas(0, 10)
    with pytest.raises(ValueError):
        Color(2, 0, 0)
    with pytest.raises(ValueError):
        Style(line_width=-1)
