"""Solid style descriptions, explicit missing paint, and input validation."""

from dataclasses import FrozenInstanceError, replace

import pytest

from pdl.author.style.color import BLACK, Color
from pdl.author.style.style import Style


def test_constructor_defaults_form_a_complete_style() -> None:
    style = Style()
    assert style.stroke == BLACK
    assert style.fill is None
    assert style.line_width == 1
    assert style.line_cap == "butt"
    assert style.line_join == "miter"
    assert style.fill_rule == "nonzero"
    assert style.opacity == 1


def test_explicit_missing_paint_and_zero_width_are_valid() -> None:
    style = Style(stroke=None, fill=None, line_width=0)
    assert style.stroke is None
    assert style.fill is None
    assert style.line_width == 0
    fill_only = Style(stroke=None, fill=Color(1, 0, 0))
    assert fill_only.fill == Color(1, 0, 0)


def test_supported_line_and_fill_options() -> None:
    style = Style(line_cap="round", line_join="bevel", fill_rule="evenodd")
    assert style.line_cap == "round"
    assert style.line_join == "bevel"
    assert style.fill_rule == "evenodd"
    assert Style(line_cap="square", line_join="round").line_cap == "square"


@pytest.mark.parametrize("opacity", [0, 0.5, 1])
def test_opacity_accepts_the_closed_unit_interval(opacity: float) -> None:
    assert Style(opacity=opacity).opacity == opacity


@pytest.mark.parametrize("value", [-1, float("nan"), float("inf"), -float("inf")])
def test_line_width_rejects_negative_and_nonfinite_values(value: float) -> None:
    with pytest.raises(ValueError, match="Line width"):
        Style(line_width=value)


@pytest.mark.parametrize("value", [-0.1, 1.1, float("nan"), float("inf"), -float("inf")])
def test_opacity_rejects_invalid_values(value: float) -> None:
    with pytest.raises(ValueError, match="Opacity"):
        Style(opacity=value)


def test_unknown_named_options_are_rejected() -> None:
    with pytest.raises(ValueError, match="line cap"):
        Style(line_cap="pointed")  # pyright: ignore[reportArgumentType]
    with pytest.raises(ValueError, match="line join"):
        Style(line_join="smooth")  # pyright: ignore[reportArgumentType]
    with pytest.raises(ValueError, match="fill rule"):
        Style(fill_rule="automatic")  # pyright: ignore[reportArgumentType]


def test_style_changes_create_independent_values() -> None:
    original = Style(stroke=None, fill=Color(1, 0, 0), opacity=0.5)
    updated = replace(original, fill=Color(0, 0, 1))
    assert original.fill == Color(1, 0, 0)
    assert updated.fill == Color(0, 0, 1)
    assert updated.stroke is None
    assert updated.opacity == 0.5
    with pytest.raises(FrozenInstanceError):
        setattr(original, "opacity", 1)
