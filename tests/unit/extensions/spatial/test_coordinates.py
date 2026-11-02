"""Public 3D coordinate and frame behavior."""

import pytest

from pdl.extensions.spatial import CoordinateSystem3D, Point3D, Transform3D, Vector3D


def xyz(point: Point3D | Vector3D) -> tuple[float, float, float]:
    return point.x, point.y, point.z


def test_composition_inverse_and_frame_conversion() -> None:
    transform = (
        Transform3D.translate(4, -3, 7)
        @ Transform3D.rotate(63, Vector3D(1, 2, 3))
        @ Transform3D.scale(2, 3, 4)
    )
    point = Point3D(2, 5, -1)
    assert xyz(transform.inverse().apply(transform.apply(point))) == pytest.approx(xyz(point))
    world = CoordinateSystem3D()
    local = world.child(transform)
    child = local.child(Transform3D.translate(1, 0, 0))
    assert xyz(child.convert_point(Point3D(0, 0, 0), world)) == pytest.approx(
        xyz(transform.apply(Point3D(1, 0, 0)))
    )
    assert xyz(local.convert_vector(Vector3D(1, 0, 0), world)) == pytest.approx(
        xyz(transform.apply_vector(Vector3D(1, 0, 0)))
    )


def test_right_hand_rotation_and_invalid_inputs() -> None:
    assert xyz(Transform3D.rotate(90).apply(Point3D(1, 0, 0))) == pytest.approx((0, 1, 0))
    with pytest.raises(ValueError):
        Transform3D.scale(0).inverse()
    with pytest.raises(ValueError):
        Transform3D.rotate(10, Vector3D(0, 0, 0))
    with pytest.raises(ValueError):
        Point3D(float("nan"), 0, 0)
