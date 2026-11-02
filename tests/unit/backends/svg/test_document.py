"""Backend semantics, fallback and real TikZ compilation."""

from typing import Literal
from xml.etree import ElementTree as ET

import pytest

from pdl import Canvas, Color, Entity, Style
from pdl.author.geometry import Bounds, Geometry
from pdl.author.geometry import Path as Path


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
    class Custom(Geometry):
        def to_path(self) -> Path:
            return Path().move_to((1, 2)).line_to((3, 4))

    canvas = Canvas(10, 10)
    canvas.draw(Entity(Custom()))
    assert 'd="M 1 2 L 3 4"' in canvas.render()
    assert "(1,2) -- (3,4)" in canvas.render("tikz")


@pytest.mark.parametrize("backend", ["svg", "tikz"])
def test_geometry_membership_does_not_guarantee_render_support(
    backend: Literal["svg", "tikz"],
) -> None:
    class Custom(Geometry):
        @property
        def layout_bounds(self) -> Bounds:
            return Bounds(1, 2, 3, 4)

    canvas = Canvas(10, 10).add(Entity(Custom()))
    with pytest.raises(TypeError, match="Unsupported render geometry: Custom"):
        canvas.render(backend)
