"""Deferred dependencies, coordinate spaces and per-render cache lifetimes."""

from dataclasses import dataclass, replace
from xml.etree import ElementTree as ET

import pytest

from pdl import (
    AnchorRef,
    Canvas,
    Connection,
    Drawing,
    Font,
    Group,
    Node,
    Point,
    Rectangle,
    RendererConfig,
    Text,
    Transform,
    bounds,
)
from pdl.scene.evaluation import layout_session


def test_authoring_needs_no_canvas_or_font_discovery() -> None:
    source = Node(Text("Source"))
    destination = Node(Text("Destination"), position=source.anchor("east") + (30, 0))
    connection = Connection(source.anchor("east"), destination.anchor("west"))
    assert isinstance(connection.start, AnchorRef)
    with pytest.raises(ValueError, match="Specify"):
        bounds(connection)


def test_dependency_order_is_independent_of_paint_order(font: Font) -> None:
    source = Node(Text("Source"), position=(20, 20))
    destination = Node(Text("Destination"), position=source.anchor("east") + (40, 0))
    route = Connection(source.anchor("east"), destination.anchor("west"), arrow_end=False)
    canvas = Canvas(100, 50)
    canvas.draw(route)
    canvas.draw(destination)
    canvas.draw(source)
    output = ET.fromstring(canvas.render(renderer=RendererConfig(fonts=(font,))))[0]
    assert output[0].tag.endswith("path")
    assert any(element.tag.endswith("text") for element in output[-1].iter())
    assert canvas.drawings[0].geometry is route
    with canvas.typography((font,)), layout_session() as context:
        start = context.point(source.anchor("east"))
        assert context.point(destination.anchor()) == Point(start.x + 40, start.y)
        assert bounds(route).left == start.x


def test_new_render_recomputes_endpoints_without_modifying_authoring(font: Font) -> None:
    source = Node(Text("A long label"), position=(30, 20))
    connection = Connection(source.anchor("east"), (90, 20), arrow_end=False)
    canvas = Canvas(100, 50)
    canvas.draw(connection)
    canvas.draw(source)

    from pdl.typography.plain import TextLayout

    original = Text.layout
    getter = original.fget
    assert getter is not None

    # Simulate a second renderer's wider font metrics without relying on
    # specific fonts installed on the test host.
    with pytest.MonkeyPatch.context() as patch:
        first = canvas.render(renderer=RendererConfig(fonts=(font,)))

        def wider(text: Text) -> TextLayout:
            layout = getter(text)
            return replace(layout, box=layout.box.expanded(5))

        patch.setattr(Text, "layout", property(wider))
        second = canvas.render(renderer=RendererConfig(fonts=(font,)))
    assert first != second
    first_path = ET.fromstring(first)[0][0].attrib["d"]
    second_path = ET.fromstring(second)[0][0].attrib["d"]
    assert first_path != second_path
    assert canvas.render(renderer=RendererConfig(fonts=(font,))) == first
    assert connection.start is not None and isinstance(connection.start, AnchorRef)


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
    assert canvas.drawings[1] is first
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


@dataclass
class MutableComposite:
    children: tuple[Drawing, ...] = ()

    def decompose(self) -> tuple[Drawing, ...]:
        return self.children


def test_dependency_cycle_reports_anchor_and_bounds() -> None:
    component = MutableComposite()
    connection = Connection(AnchorRef(component, "east"), (10, 0))
    component.children = (Drawing(connection),)
    canvas = Canvas(50, 30)
    canvas.draw(connection)
    with pytest.raises(ValueError, match=r"Cyclic layout dependency:.*anchor.*bounds"):
        canvas.render()


def test_composite_cycle_with_changing_transform_is_rejected() -> None:
    component = MutableComposite()
    component.children = (Drawing(component, transform=Transform.translate(1, 0)),)
    with pytest.raises(ValueError, match="Cyclic composite"):
        bounds(component)


def test_shared_dependencies_are_evaluated_once_per_render() -> None:
    class Counted:
        calls = 0

        def decompose(self) -> tuple[Drawing, ...]:
            self.calls += 1
            return (Drawing(Rectangle((10, 10), 5, 5)),)

    target = Counted()
    canvas = Canvas(60, 30)
    canvas.draw(Connection(AnchorRef(target, "east"), (40, 12)))
    canvas.draw(Connection(AnchorRef(target, "north"), (12, 25)))
    canvas.draw(target)
    canvas.render()
    assert target.calls == 1
    canvas.render()
    assert target.calls == 2


def test_degenerate_references_fail_at_evaluation() -> None:
    target = Group((Drawing(Rectangle((0, 0), 5, 5)),))
    connection = Connection(target.anchor(), target.anchor())
    canvas = Canvas(20, 20)
    canvas.draw(connection)
    with pytest.raises(ValueError, match="distinct"):
        canvas.render()
