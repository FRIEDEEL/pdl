"""Backend semantics, fallback and real TikZ compilation."""

from xml.etree import ElementTree as ET

from pdl import Canvas, Color, Entity, Style
from pdl import PathGeometry as Path


def test_open_fill_does_not_close_stroke() -> None:
    canvas = Canvas(10, 10)
    canvas.draw(
        Entity(Path().move_to((1, 1)).line_to((8, 1)).line_to((4, 8))),
        Style(fill=Color(1, 0, 0), fill_rule="evenodd"),
    )
    element = ET.fromstring(canvas.render())[0][0]
    assert "Z" not in element.attrib["d"]
    assert element.attrib["fill-rule"] == "evenodd"
    assert "cycle" not in canvas.render("tikz")
    assert "even odd rule" in canvas.render("tikz")


def test_custom_geometry_fallback() -> None:
    class Custom:
        def to_path(self) -> Path:
            return Path().move_to((1, 2)).line_to((3, 4))

    canvas = Canvas(10, 10)
    canvas.draw(Entity(Custom()))
    assert 'd="M 1 2 L 3 4"' in canvas.render()
    assert "(1,2) -- (3,4)" in canvas.render("tikz")
