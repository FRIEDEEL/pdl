"""Public mutable objects, explicit frames, and capture isolation."""

import pytest

from pdl import (
    Canvas,
    Circle,
    Entity,
    Frame,
    Gather,
    Group,
    Line,
    Path,
    Point,
    Rectangle,
    ReferencePoint,
    Style,
    Text,
    Transform,
    Vector,
    bounds,
)
from pdl.scene.composition import walk


def test_concrete_objects_share_entity_and_mutate_in_place() -> None:
    circle = Circle((20, 10), 5)
    assert isinstance(circle, Entity)
    assert isinstance(Line((0, 0), (1, 0)), Entity)
    assert isinstance(Text("A"), Entity)
    assert isinstance(Group(), Entity)
    assert circle.translate(5, 0) is circle
    assert circle.scale(2, 1) is circle
    assert bounds(circle).anchor() == Point(25, 10)
    assert bounds(circle).width == pytest.approx(20)
    assert circle.center == (20, 10)
    assert circle.radius == 5


def test_explicit_pivot_and_draw_capture() -> None:
    canvas = Canvas(100, 100)
    shape = Rectangle((-1, -1), 2, 2).translate(10, 0)
    canvas.draw(shape)
    shape.rotate(90, about=(0, 0))
    canvas.draw(shape)
    boxes = [canvas.bounds(d) for d in canvas.drawings]
    assert (boxes[0].anchor().x, boxes[0].anchor().y) == pytest.approx((10, 0))
    assert (boxes[1].anchor().x, boxes[1].anchor().y) == pytest.approx((0, 10))
    before = canvas.render()
    shape.translate(50, 0)
    assert canvas.render() == before
    from inspect import signature

    assert "center" not in signature(shape.rotate).parameters
    with pytest.raises(TypeError, match="base class"):
        Entity()


def test_copy_group_and_member_are_independent() -> None:
    shape = Circle((10, 10), 2)
    group = Group((shape,))
    duplicate = group.copy()
    duplicate.translate(30, 0)
    duplicate.members[0].scale(2)
    assert bounds(group).anchor() == Point(10, 10)
    assert bounds(group).width == pytest.approx(4)
    assert bounds(duplicate).anchor() == Point(40, 10)
    assert bounds(duplicate).width == pytest.approx(8)
    detached = shape.copy().translate(0, 10)
    assert detached.parent is None
    assert bounds(detached).anchor() == Point(10, 20)
    assert bounds(shape).anchor() == Point(10, 10)


def test_equal_geometry_members_remain_distinct() -> None:
    a, b = Circle((0, 0), 2), Circle((0, 0), 2)
    group = Group((a, b))
    group.remove(b)
    assert group.members == (a,)
    assert a.parent is group and b.parent is None


def test_path_can_continue_building_after_transform_and_draw() -> None:
    path = Path().move_to((0, 0)).line_to((2, 0)).translate(10, 0)
    canvas = Canvas(50, 30)
    canvas.draw(path)
    path.line_to((2, 3))
    canvas.draw(path)
    assert canvas.bounds(canvas.drawings[0]).height == 0
    assert canvas.bounds(canvas.drawings[1]).height == 3
    assert bounds(path).left == 10


def test_frame_math_and_independent_default_frame() -> None:
    frame = Frame((5, 3), Vector(2, 0), Vector(1, 3))
    assert frame.point(2, 4).resolve() == Point(13, 15)
    assert frame.point(2, 4).resolve(frame.space) == Point(2, 4)
    assert frame.vector(2, 4).resolve() == Vector(8, 12)
    frame.translate(10, 0)
    assert frame.origin == Point(15, 3)
    assert frame.x_basis == Vector(2, 0)
    shape = Circle((20, 10), 2)
    reference = shape.frame
    shape.translate(5, 0).rotate(30)
    assert reference.origin == Point(0, 0)
    assert reference.x_basis == Vector(1, 0)
    assert reference.y_basis == Vector(0, 1)


def test_gather_and_group_transform_nonpainting_references() -> None:
    shape = Circle((10, 10), 2)
    frame = Frame((10, 10))
    mark = ReferencePoint((1000, 1000))
    Gather(shape, frame, mark).translate(5, 3)
    assert frame.origin == Point(15, 13)
    assert mark.position == Point(1005, 1003)
    group = Group((shape, frame, mark))
    group.rotate(90, about=frame.origin)
    assert (frame.x_basis.x, frame.x_basis.y) == pytest.approx((0, 1))
    assert bounds(group).width == pytest.approx(4)
    assert bounds(group).height == pytest.approx(4)
    canvas = Canvas(50, 50)
    canvas.draw(group)
    leaves = tuple(walk(canvas.drawings))
    assert len(leaves) == 1
    assert isinstance(leaves[0].geometry, Circle)
    assert canvas.render().count("<circle") == 1
    empty = Canvas(50, 50)
    empty.draw(frame.copy())
    empty.draw(mark.copy())
    assert tuple(walk(empty.drawings)) == ()
    assert bounds(frame).is_empty


def test_frame_reference_follows_until_draw_then_freezes() -> None:
    frame = Frame((10, 0))
    shape = Circle((0, 0), 1).move_to(frame.point(2, 0))
    frame.translate(5, 0)
    canvas = Canvas(50, 30)
    canvas.draw(shape)
    assert canvas.bounds(canvas.drawings[0]).anchor() == Point(17, 0)
    frame.translate(5, 0)
    assert bounds(shape).anchor() == Point(22, 0)
    assert canvas.bounds(canvas.drawings[0]).anchor() == Point(17, 0)


def test_frame_visualization_is_an_independent_painted_snapshot() -> None:
    frame = Frame((10, 10), (2, 0), (0, 1))
    graphic = frame.visualize(axis_length=5)
    box = bounds(graphic)
    assert box.right == 20
    assert box.top == 15
    frame.translate(100, 100)
    assert bounds(graphic) == box
    canvas = Canvas(50, 30)
    canvas.draw(graphic)
    assert canvas.render().count("<path") == 2
    assert canvas.render().count("<circle") == 1
    with pytest.raises(ValueError, match="axis_length"):
        frame.visualize(axis_length=0)


def test_transformed_text_remains_native_and_measures_later() -> None:
    text = Text("Stretch").scale(2, 1).rotate(15)
    assert isinstance(text, Entity)
    canvas = Canvas(100, 60, mode="fit")
    canvas.draw(text)
    svg = canvas.render()
    assert "<text" in svg and 'transform="matrix(' in svg
    source = canvas.render("tikz")
    assert "transform shape" in source


def test_styles_and_affine_matrix_are_shared_operations() -> None:
    line = Line((0, 0), (10, 0)).set_style(Style(line_width=2))
    line.apply_transform(Transform.translate(5, 3))
    assert bounds(line).left == 5
    assert bounds(line).bottom == 3
    canvas = Canvas(30, 20)
    canvas.draw(line)
    assert 'stroke-width="2"' in canvas.render()


@pytest.mark.parametrize("frame_first", [False, True])
def test_gather_shared_reference_is_independent_of_member_order(frame_first: bool) -> None:
    frame = Frame((10, 0))
    shape = Circle((0, 0), 1).move_to(frame.point(2, 0))
    members = (frame, shape) if frame_first else (shape, frame)
    Gather(*members).translate(5, 0)
    assert frame.origin == Point(15, 0)
    assert bounds(shape).anchor() == Point(17, 0)


def test_group_center_transform_defers_text_measurement() -> None:
    group = Group((Text("Deferred group"),)).rotate(30).scale(2).translate(10, 0)
    duplicate = group.copy()
    canvas = Canvas(100, 60, mode="fit")
    canvas.draw(group)
    before = canvas.render()
    duplicate.translate(20, 0)
    assert canvas.render() == before
    assert "<text" in before


def test_copy_after_draw_keeps_layer_identity_and_detaches_frame_references() -> None:
    frame = Frame((10, 0))
    shape = Circle((0, 0), 1).move_to(frame.point(2, 0))
    canvas = Canvas(100, 60)
    canvas.draw(shape)
    duplicate = shape.copy()
    frame.translate(10, 0)
    duplicate.translate(0, 10)
    canvas.draw(duplicate)
    assert canvas.bounds(canvas.drawings[0]).anchor() == Point(12, 0)
    assert canvas.bounds(canvas.drawings[1]).anchor() == Point(12, 10)
    assert bounds(shape).anchor() == Point(22, 0)


def test_geometry_edits_affect_future_draws_without_losing_transform() -> None:
    shape = Circle((0, 0), 2).translate(10, 0)
    canvas = Canvas(100, 60)
    canvas.draw(shape)
    shape.radius = 4
    canvas.draw(shape)
    assert canvas.bounds(canvas.drawings[0]).width == 4
    assert canvas.bounds(canvas.drawings[1]).width == 8
    assert bounds(shape).anchor() == Point(10, 0)


def test_resolved_leaf_can_be_copied_back_to_an_editable_object() -> None:
    canvas = Canvas(100, 60)
    leaf = canvas.resolve(Circle((10, 10), 2)).decompose()[0].geometry
    assert isinstance(leaf, Circle)
    editable = leaf.copy().translate(20, 0)
    assert bounds(editable).anchor() == Point(30, 10)
    assert bounds(leaf).anchor() == Point(10, 10)


def test_automatic_layers_allow_reuse_but_explicit_layers_remain_canvas_bound() -> None:
    shape = Circle((10, 10), 2)
    first, second = Canvas(30, 20), Canvas(30, 20)
    first.draw(shape)
    second.draw(shape)
    assert first.render() == second.render()
    group = Group((shape,))
    second.draw(group)
    with pytest.warns(UserWarning, match="promoted"):
        shape.set_layer(second.layers[0])
    with pytest.raises(ValueError, match="one Canvas"):
        Canvas(30, 20).draw(group)


def test_direct_coordinate_placement_supports_shapes_and_groups() -> None:
    from pdl import CoordinateSystem

    local = CoordinateSystem(transform=Transform.translate(10, 5))
    shape = Circle((2, 3), 1).in_space(local)
    group = Group((Circle((2, 3), 1),)).in_space(local)
    canvas = Canvas(60, 40)
    assert canvas.bounds(shape).anchor() == Point(12, 8)
    assert canvas.bounds(group).anchor() == Point(12, 8)
    canvas.draw(group)
    canvas.map(local, Transform.translate(20, 5))
    assert canvas.bounds(canvas.drawings[0]).anchor() == Point(22, 8)
