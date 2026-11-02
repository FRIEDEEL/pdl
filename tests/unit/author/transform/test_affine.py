"""Affine mapping, composition order, explicit pivots, and inverse behavior."""

from dataclasses import FrozenInstanceError

import pytest

from pdl.author.transform.affine import (
    AffineTransform,
    Reflection,
    Rotation,
    Scaling,
    Shear,
    Translation,
)


def test_identity_and_homogeneous_matrix() -> None:
    identity = AffineTransform()
    assert identity.apply((3, -7)) == (3, -7)
    transform = AffineTransform(a=2, b=3, c=4, d=5, e=6, f=7)
    assert transform.matrix == ((2, 4, 6), (3, 5, 7), (0, 0, 1))
    assert transform.apply((10, 20)) == (106, 137)


def test_concrete_mappings() -> None:
    assert Translation(5, -3).apply((2, 4)) == (7, 1)
    assert Rotation(90).apply((2, 0)) == pytest.approx((0, 2))
    assert Scaling(3).apply((2, 4)) == (6, 12)
    assert Scaling(-2, 3).apply((2, 4)) == (-4, 12)
    assert Shear(x_factor=2, y_factor=3).apply((2, 4)) == (10, 10)
    assert Reflection().apply((2, 4)) == (2, -4)
    assert Reflection(45).apply((2, 4)) == pytest.approx((4, 2))
    assert Reflection(90).apply((2, 4)) == pytest.approx((-2, 4))


def test_composition_applies_right_operand_first() -> None:
    translated_rotation = Translation(10, 0) @ Rotation(90)
    rotated_translation = Rotation(90) @ Translation(10, 0)
    assert type(translated_rotation) is AffineTransform
    assert translated_rotation.apply((1, 0)) == pytest.approx((10, 1))
    assert rotated_translation.apply((1, 0)) == pytest.approx((0, 11))


@pytest.mark.parametrize(
    "transform",
    [
        AffineTransform(),
        Translation(12, -8),
        Rotation(37),
        Scaling(2, -3),
        Shear(0.4, 0.2),
        Reflection(23),
        Translation(5, 7) @ Rotation(-63) @ Shear(0.2) @ Scaling(3, 2),
    ],
)
def test_inverse_round_trip(transform: AffineTransform) -> None:
    position = (3.5, -7.25)
    inverse = transform.inverse()
    assert inverse.apply(transform.apply(position)) == pytest.approx(position)
    assert transform.apply(inverse.apply(position)) == pytest.approx(position)


@pytest.mark.parametrize("scale", [1e-200, 1e200])
def test_inverse_avoids_unnecessary_scale_overflow_and_underflow(scale: float) -> None:
    transform = Scaling(scale)
    assert transform.inverse().apply(transform.apply((1, -2))) == pytest.approx((1, -2))


def test_inverse_handles_different_row_scales() -> None:
    transform = Scaling(1e200, 1e-200)
    assert transform.inverse().apply(transform.apply((1, -2))) == pytest.approx((1, -2))


@pytest.mark.parametrize("transform", [Scaling(0, 2), AffineTransform(a=1, b=2, c=2, d=4)])
def test_singular_mappings_are_valid_but_have_no_inverse(transform: AffineTransform) -> None:
    assert all(isinstance(value, (int, float)) for value in transform.apply((1, 2)))
    with pytest.raises(ValueError, match="singular"):
        transform.inverse()


def test_explicit_pivots_do_not_modify_the_original_transform() -> None:
    pivot = (3, 7)
    rotation = Rotation(90)
    around = rotation.around(pivot)
    assert around.apply(pivot) == pytest.approx(pivot)
    assert around.apply((4, 7)) == pytest.approx((3, 8))
    assert rotation.apply((1, 0)) == pytest.approx((0, 1))
    assert Scaling(2, 3).around(pivot).apply((4, 8)) == (5, 10)
    assert Translation(2, 5).around(pivot) == Translation(2, 5)
    assert Reflection().around(pivot).apply((4, 9)) == (4, 5)


def test_affine_values_are_immutable_and_equal_across_subclasses() -> None:
    transform = Translation(2, 3)
    equivalent = AffineTransform(e=2, f=3)
    assert transform == equivalent
    assert hash(transform) == hash(equivalent)
    assert transform != (2, 3)
    with pytest.raises(FrozenInstanceError):
        setattr(transform, "e", 10)


@pytest.mark.parametrize("value", [float("nan"), float("inf"), -float("inf")])
def test_nonfinite_parameters_and_coordinates_are_rejected(value: float) -> None:
    with pytest.raises(ValueError, match="finite"):
        AffineTransform(c=value)
    with pytest.raises(ValueError, match="finite"):
        Translation(value, 0)
    with pytest.raises(ValueError, match="finite"):
        Rotation(value)
    with pytest.raises(ValueError, match="finite"):
        Scaling(1, value)
    with pytest.raises(ValueError, match="finite"):
        Shear(y_factor=value)
    with pytest.raises(ValueError, match="finite"):
        Reflection(value)
    with pytest.raises(ValueError, match="finite"):
        AffineTransform().apply((value, 0))
    with pytest.raises(ValueError, match="finite"):
        Rotation(30).around((0, value))


def test_overflow_is_reported_instead_of_returning_nonfinite_results() -> None:
    with pytest.raises(ValueError, match="finite"):
        Scaling(1e308).apply((2, 3))
    with pytest.raises(ValueError, match="finite"):
        _ = Scaling(1e308) @ Scaling(2)
