"""Deferred dependencies, coordinate spaces and per-render cache lifetimes."""

from dataclasses import dataclass
from xml.etree import ElementTree as ET

import pytest

from pdl import (
    Canvas,
    Connection,
    Drawing,
    Font,
    Group,
    Node,
    Point,
    Rectangle,
    RendererConfig,
    Style,
    Text,
    Transform,
    bounds,
)
from pdl.author.measurement import layout_session


def test_authoring_queries_produce_fixed_numerical_points() -> None:
    source = Node(Text("Source"))
    destination = Node(Text("Destination"), position=source.anchor("east") + (30, 0))
    connection = Connection(source.anchor("east"), destination.anchor("west"))
    assert isinstance(connection.start, Point)
    before = bounds(connection)
    source.translate(50, 0)
    assert bounds(connection) == before


def test_dependency_order_is_independent_of_paint_order(font: Font) -> None:
    source = Node(Text("Source", font), position=(20, 20))
    destination = Node(Text("Destination", font), position=source.anchor("east") + (40, 0))
    route = Connection(source.anchor("east"), destination.anchor("west"), arrow_end=False)
    canvas = Canvas(100, 50)
    canvas.draw(route)
    canvas.draw(destination)
    canvas.draw(source)
    output = ET.fromstring(canvas.render(renderer=RendererConfig(fonts=(font,))))[0]
    assert output[0].tag.endswith("path")
    assert any(element.tag.endswith("text") for element in output[-1].iter())
    assert canvas.drawings[0].geometry is not route
    assert canvas.bounds(canvas.drawings[0]) == canvas.bounds(route)
    with canvas.typography((font,)), layout_session() as context:
        start = context.point(source.anchor("east"))
        assert context.point(destination.anchor()) == Point(start.x + 40, start.y)
        assert bounds(route).left == start.x


def test_draw_records_keep_layout_after_later_label_edits(font: Font) -> None:
    source = Node(Text("Short", font), position=(30, 20))
    connection = Connection(source.anchor("east"), (90, 20), arrow_end=False)
    canvas = Canvas(100, 50)
    canvas.draw(connection)
    canvas.draw(source)
    first = canvas.render()
    assert isinstance(source.label, Text)
    source.label.text = "A much longer label"
    assert canvas.render() == first
    assert connection.start != source.anchor("east")
    canvas.draw(source)
    assert canvas.render() != first


def test_placed_instances_have_distinct_transformed_anchors(font: Font) -> None:
    definition = Node(Text("P", font), shape="circle")
    first = Drawing(definition, transform=Transform.translate(20, 20))
    second = first.transformed(Transform.translate(50, 0) @ Transform.rotate(90))
    with layout_session() as context:
        local = context.point(definition.anchor("east"))
        assert context.point(first.anchor("east")) == first.transform.apply(local)
        assert context.point(second.anchor("east")) == second.transform.apply(local)
    canvas = Canvas(100, 100)
    canvas.draw(Connection(first.anchor("east"), second.anchor("east")))
    canvas.draw(first)
    canvas.draw(second)
    assert canvas.drawings[1] is not first
    assert canvas.bounds(canvas.drawings[1]) == canvas.bounds(first)
    assert canvas.render().count("<circle") == 2


def test_internal_references_follow_reused_group_placement(font: Font) -> None:
    node = Node(Text("P", font), position=(10, 10))
    link = Connection(node.anchor("east"), (35, 10), arrow_end=False)
    definition = Group((Drawing(link), Drawing(node)))
    canvas = Canvas(100, 60)
    canvas.draw(definition)
    canvas.draw(definition.transformed(Transform.translate(50, 20)))
    output = ET.fromstring(canvas.render())[0]
    paths = [element for element in output if element.tag.endswith("path")]
    assert len(paths) == 2 and paths[0].attrib["d"] != paths[1].attrib["d"]


def test_nested_child_anchor_uses_the_complete_instance_transform(font: Font) -> None:
    node = Node(Text("Port", font), position=(10, 5))
    inner = Group((Drawing(node),), Transform.rotate(25))
    outer = Group((Drawing(inner),), Transform.translate(30, 20))
    instance = Drawing(outer, transform=Transform.translate(50, 20))
    port = instance.child(0).child(0)
    with layout_session() as context:
        local = context.point(node.anchor("west"))
        expected = (instance.transform @ outer.transform @ inner.transform).apply(local)
        assert context.point(port.anchor("west")) == expected
    assert isinstance(port.geometry, Node)
    assert port.geometry is not node
    assert isinstance(port.geometry.label, Text) and isinstance(node.label, Text)
    assert port.geometry.label.text == node.label.text
    with pytest.raises(TypeError, match="Group"):
        port.child(0)


def test_child_access_does_not_measure_or_discover_fonts() -> None:
    node = Node(Text("Unmeasured"))
    group = Group((Drawing(node),), Transform.translate(20, 30))
    connection = Connection(group.child(0).anchor("west"), (0, 30))
    assert isinstance(connection.start, Point)


def test_child_instances_keep_inherited_and_explicit_paint() -> None:
    inherited, explicit = Style(line_width=2), Style(line_width=3)
    group = Group((Drawing(Rectangle((0, 0), 1, 1)), Drawing(Rectangle((2, 0), 1, 1), explicit)))
    instance = Drawing(group, inherited)
    assert instance.child(0).style is inherited
    assert instance.child(1).style is explicit


@dataclass
class MutableComposite:
    children: tuple[Drawing, ...] = ()

    def decompose(self) -> tuple[Drawing, ...]:
        return self.children


def test_composition_cycle_is_rejected_on_submission() -> None:
    component = MutableComposite()
    component.children = (Drawing(component),)
    with pytest.raises(ValueError, match="Cyclic composite"):
        Canvas(50, 30).draw(component)


def test_composite_cycle_with_changing_transform_is_rejected() -> None:
    component = MutableComposite()
    component.children = (Drawing(component, transform=Transform.translate(1, 0)),)
    with pytest.raises(ValueError, match="Cyclic composite"):
        bounds(component)


def test_custom_component_is_captured_once_and_not_revisited_by_backends() -> None:
    class Counted:
        calls = 0

        def decompose(self) -> tuple[Drawing, ...]:
            self.calls += 1
            return (Drawing(Rectangle((10, 10), 5, 5)),)

    component = Counted()
    canvas = Canvas(60, 30)
    canvas.draw(component)
    assert component.calls == 1
    canvas.render()
    canvas.render("tikz")
    assert component.calls == 1


def test_degenerate_connections_fail_at_construction() -> None:
    target = Rectangle((0, 0), 5, 5)
    with pytest.raises(ValueError, match="distinct"):
        Connection(target.anchor(), target.anchor())
