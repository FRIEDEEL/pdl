"""The general transformation contract does not require a matrix or inverse."""

import pytest

from pdl.author.transform.affine import AffineTransform
from pdl.author.transform.base import Transform


class Bend(Transform):
    """A test-only nonlinear map with no affine representation."""

    def apply(self, position: tuple[float, float]) -> tuple[float, float]:
        x, y = position
        return x, y + x * x


def test_transform_is_abstract() -> None:
    with pytest.raises(TypeError, match="abstract"):
        Transform()  # pyright: ignore[reportAbstractUsage]


def test_general_transform_can_be_nonlinear() -> None:
    transform: Transform = Bend()
    assert transform.apply((2, 3)) == (2, 7)
    assert not hasattr(transform, "matrix")
    assert not hasattr(transform, "inverse")


def test_affine_composition_rejects_unsupported_general_mappings() -> None:
    with pytest.raises(TypeError):
        _ = AffineTransform() @ Bend()
