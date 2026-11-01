"""Gradient validation does not depend on drawing objects or output adapters."""

import pytest

from pdl.author.style.color import Color
from pdl.author.style.gradient import ColorStop, LinearGradient, RadialGradient

STOPS = (ColorStop(0, Color(0, 0, 0)), ColorStop(1, Color(1, 1, 1)))


def test_gradient_stops_and_coordinates_are_validated() -> None:
    assert LinearGradient(STOPS).stops is STOPS
    assert RadialGradient(STOPS).radius == 0.5
    with pytest.raises(ValueError):
        LinearGradient(STOPS, start=(1, 1), end=(1, 1))
    with pytest.raises(ValueError):
        LinearGradient(STOPS, end=(float("nan"), 0))
    with pytest.raises(ValueError):
        RadialGradient(STOPS, radius=0)
    with pytest.raises(ValueError):
        LinearGradient((STOPS[1], STOPS[0]))
