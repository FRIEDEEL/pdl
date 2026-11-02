"""Layer identities retain stable ordering across insertions and state captures."""

import pytest

from pdl import Canvas, Circle, Gather, Group, Layer


def radius(canvas: Canvas) -> list[float]:
    from pdl.author.entity.capture import walk
    from pdl.author.geometry.shapes import Circle

    return [d.geometry.radius for d in walk(canvas.drawings) if isinstance(d.geometry, Circle)]


def test_integer_assignment_capture_and_layer_insertions() -> None:
    canvas = Canvas(100, 100)
    a, b = Circle((10, 10), 1), Circle((10, 10), 2)
    a.set_layer(1)
    canvas.draw(a)
    canvas.draw(b)
    assert radius(canvas) == [2, 1]
    top = canvas.layers[1]
    middle = canvas.layers.insert_below(top)
    assert canvas.layers[2] is top
    assert a.layer is top
    canvas.layers.move_below(top, canvas.layers[0])
    assert radius(canvas) == [1, 2]
    a.set_layer(middle)
    canvas.draw(a)
    assert radius(canvas) == [1, 2, 1]


def test_group_uses_highest_layer_and_preserves_internal_order() -> None:
    canvas = Canvas(100, 100)
    bottom, top = canvas.layers[0], canvas.layers[1]
    a, b = Circle((10, 10), 1), Circle((10, 10), 2)
    bottom.add(a)
    top.add(b)
    group = Group(b, a)
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

    from pdl.author.entity.base import Entity as Graphic

    layer = Layer(1)
    a = Circle((0, 0), 1)
    layer.add(a)
    selection = layer.to_gather()
    b = Circle((0, 0), 2)
    layer.add(b)
    assert selection.members == (a,)
    canvas = Canvas(100, 100)
    canvas.draw(a)
    with pytest.raises(ValueError, match="one Canvas"):
        Canvas(100, 100).draw(a)
    for invalid in (layer, Gather(a)):
        with pytest.raises(TypeError):
            canvas.draw(cast(Graphic, invalid))


def test_neighbors_at_boundaries_and_before_adoption_do_not_create_layers() -> None:
    detached = Layer(5)
    assert detached.upper is None
    assert detached.lower is None
    canvas = Canvas(100, 60)
    only = canvas.layers[0]
    assert only.upper is None
    assert only.lower is None
    assert len(canvas.layers) == 1
    canvas.layers.adopt(detached)
    assert only.upper is detached
    assert detached.lower is only
    assert detached.upper is None
    assert len(canvas.layers) == 2


def test_neighbors_follow_insertions_and_moves() -> None:
    canvas = Canvas(100, 60)
    bottom = canvas.layers[0]
    top = canvas.layers.insert_above(bottom, name="top")
    middle = canvas.layers.insert_below(top, name="middle")
    assert middle.lower is bottom
    assert middle.upper is top
    assert top.position == 2
    canvas.layers.move_above(bottom, top)
    assert middle.lower is None
    assert middle.upper is top
    assert top.upper is bottom
    assert bottom.upper is None
    canvas.layers.move_below(bottom, middle)
    assert bottom.lower is None
    assert bottom.upper is middle
    assert middle.upper is top
    canvas.layers.move_above(middle, middle)
    assert middle.lower is bottom
    assert len(canvas.layers) == 3


def test_move_rejects_foreign_layers_without_changing_order() -> None:
    canvas = Canvas(100, 60)
    bottom, top = canvas.layers[0], canvas.layers[1]
    foreign = Layer()
    for move in (canvas.layers.move_above, canvas.layers.move_below):
        with pytest.raises(ValueError):
            move(top, foreign)
        with pytest.raises(ValueError):
            move(foreign, top)
    assert bottom.upper is top
    assert top.lower is bottom
