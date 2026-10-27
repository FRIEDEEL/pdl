"""Gradient contracts and transformed dual-backend resource output."""

from xml.etree import ElementTree as ET

import pytest

from pdl import (
    Canvas,
    Color,
    ColorStop,
    Drawing,
    LinearGradient,
    Path,
    RadialGradient,
    Rectangle,
    Style,
    Text,
    Transform,
)

STOPS = (ColorStop(0, Color(1, 0, 0)), ColorStop(0.3, Color(1, 1, 1)), ColorStop(1, Color(0, 0, 1)))


def test_gradient_validation() -> None:
    for stops in ((), STOPS[1:], (STOPS[0], STOPS[0], STOPS[-1])):
        with pytest.raises(ValueError):
            LinearGradient(stops)
    with pytest.raises(ValueError):
        ColorStop(float("nan"), Color(0, 0, 0))
    with pytest.raises(ValueError):
        LinearGradient(STOPS, (0, 0), (0, 0))
    with pytest.raises(ValueError):
        RadialGradient(STOPS, radius=0)
    with pytest.raises(ValueError):
        Style(opacity=1.1)


@pytest.mark.parametrize("gradient", [LinearGradient(STOPS), RadialGradient(STOPS)])
def test_gradient_resources_have_unique_ids_and_follow_transform(
    gradient: LinearGradient | RadialGradient,
) -> None:
    canvas = Canvas(100, 60)
    for x in (0, 30):
        canvas.draw(
            Drawing(Rectangle((0, 0), 20, 10), Style(fill=gradient), Transform.translate(x, 5))
        )
    root = ET.fromstring(canvas.render())
    gradients = [e for e in root.iter() if e.tag.endswith(("linearGradient", "radialGradient"))]
    assert len({g.attrib["id"] for g in gradients}) == 2
    assert gradients[0].attrib["gradientTransform"] == "matrix(20 0 0 10 0 5)"
    assert gradients[1].attrib["gradientTransform"] == "matrix(20 0 0 10 30 5)"
    assert len(list(gradients[0])) == 3
    tikz = canvas.render("tikz")
    assert tikz.count("\\pgfdeclarefunctionalshading") == 2
    assert "pdlgradient0" in tikz and "pdlgradient1" in tikz


def test_gradients_respect_evenodd_and_singular_output() -> None:
    shape = Path().move_to((0, 0)).line_to((20, 0)).line_to((20, 20)).close()
    canvas = Canvas(100, 60)
    canvas.draw(
        Drawing(shape, Style(fill=LinearGradient(STOPS), fill_rule="evenodd"), Transform.scale(0))
    )
    assert "pgfdeclarefunctionalshading" not in canvas.render("tikz")
    canvas.draw(shape, Style(fill=LinearGradient(STOPS), fill_rule="evenodd"))
    assert "\\begin{scope}[even odd rule]" in canvas.render("tikz")


def test_native_text_rejects_gradient_fill() -> None:
    canvas = Canvas(100, 60)
    canvas.draw(Text("label"), Style(stroke=None, fill=LinearGradient(STOPS)))
    for backend in ("svg", "tikz"):
        with pytest.raises(ValueError, match="solid"):
            canvas.render(backend)
