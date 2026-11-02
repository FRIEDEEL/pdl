"""RGB ranges and stable, immutable color values."""

from dataclasses import FrozenInstanceError

import pytest

from pdl.author.style.color import BLACK, Color


def test_rgb_channels_and_boundary_values() -> None:
    assert BLACK == Color(0, 0, 0)
    assert Color(1, 1, 1).channels == (1, 1, 1)
    assert Color(0.2, 0.4, 0.6).channels == (0.2, 0.4, 0.6)


@pytest.mark.parametrize("value", [-0.1, 1.1, float("nan"), float("inf"), -float("inf")])
@pytest.mark.parametrize("channel", [0, 1, 2])
def test_all_rgb_channels_reject_invalid_values(value: float, channel: int) -> None:
    channels = [0.0, 0.0, 0.0]
    channels[channel] = value
    with pytest.raises(ValueError, match="RGB channels"):
        Color(*channels)


def test_color_values_are_immutable() -> None:
    value = Color(0.2, 0.4, 0.6)
    with pytest.raises(FrozenInstanceError):
        setattr(value, "red", 1)
