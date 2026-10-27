"""Layer identities retain stable ordering across insertions and state captures."""

import pytest

from pdl import Canvas, Circle, Entity, Gather, Group, Layer


def radius(canvas: Canvas) -> list[float]:
    from pdl.scene.composition import walk

    return [d.geometry.radius for d in walk(canvas.drawings) if isinstance(d.geometry, Circle)]


def test_integer_assignment_capture_and_layer_insertions() -> None:
    canvas = Canvas(100, 100)
    a, b = Entity(Circle((10, 10), 1)), Entity(Circle((10, 10), 2))
    a.set_layer(1)
    canvas.draw(a)
    canvas.draw(b)
    assert radius(canvas) == [2, 1]
    top = canvas.layers[1]
    middle = canvas.layers.insert_before(top)
    assert canvas.layers[2] is top
    assert a.layer is top
    canvas.layers.move_before(top, canvas.layers[0])
    assert radius(canvas) == [1, 2]
    a.set_layer(middle)
    canvas.draw(a)
    assert radius(canvas) == [1, 2, 1]


def test_group_uses_highest_layer_and_preserves_internal_order() -> None:
    canvas = Canvas(100, 100)
    bottom, top = canvas.layers[0], canvas.layers[1]
    a, b = Entity(Circle((10, 10), 1)), Entity(Circle((10, 10), 2))
    bottom.add(a)
    top.add(b)
    group = Group((b, a))
    assert group.layer is top
    assert group.members == (a, b)
    assert top.members == (group,)
    with pytest.warns(UserWarning, match="promoted"):
        a.set_layer(bottom)
    assert group.layer is bottom
    assert top.members == ()
    assert bottom.to_gather().members == (group,)
    group.dismiss()
    assert bottom.to_gather().members == (a, b)


def test_layer_membership_and_invalid_drawables() -> None:
    from typing import cast

    from pdl.scene.composition import Graphic

    layer = Layer(1)
    a = Entity(Circle((0, 0), 1))
    layer.add(a)
    selection = layer.to_gather()
    b = Entity(Circle((0, 0), 2))
    layer.add(b)
    assert selection.members == (a,)
    canvas = Canvas(100, 100)
    canvas.draw(a)
    with pytest.raises(ValueError, match="one Canvas"):
        Canvas(100, 100).draw(a)
    for invalid in (layer, Gather(a)):
        with pytest.raises(TypeError):
            canvas.draw(cast(Graphic, invalid))
