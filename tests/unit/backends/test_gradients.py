"""Gradients bake current coordinates without retaining object transformations."""

from xml.etree import ElementTree as ET

import pytest

from pdl import Canvas, Color, ColorStop, LinearGradient, RadialGradient, Rectangle, Style

STOPS = (ColorStop(0, Color(1, 0, 0)), ColorStop(1, Color(0, 0, 1)))


@pytest.mark.parametrize("fill", [LinearGradient(STOPS), RadialGradient(STOPS)])
def test_rotated_gradient_follows_current_geometry(fill: LinearGradient | RadialGradient) -> None:
    entity = Rectangle((0, 0), 10, 5, style=Style(fill=fill, stroke=None))
    entity.rotate(90, origin=(0, 0))
    gradient = entity.effective_style.fill
    assert isinstance(gradient, (LinearGradient, RadialGradient))
    assert gradient.frame is not None
    assert gradient.frame[1][0] == pytest.approx(0, abs=1e-10)
    assert gradient.frame[1][1] == pytest.approx(10)
    canvas = Canvas(30, 30).add(entity)
    ET.fromstring(canvas.render())
    assert "gradientTransform" in canvas.render()
    assert "pgfdeclarefunctionalshading" in canvas.render("tikz")
