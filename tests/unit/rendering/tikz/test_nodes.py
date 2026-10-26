"""Native nodes, authoring layout and affine fallback selection."""

import pytest

from pdl import Canvas, Connection, Drawing, Font, Node, Text, Transform
from pdl.rendering.formatting import number


def test_native_node_does_not_call_general_decomposition(
    font: Font, monkeypatch: pytest.MonkeyPatch
) -> None:
    def unexpected(node: Node) -> tuple[Drawing, ...]:
        raise AssertionError("Native node must not be decomposed, including preamble collection.")

    node = Node(Text("Native label", font), position=(30, 20))
    canvas = Canvas(100, 50)
    canvas.draw(Connection(node.anchor("east"), (90, 20), arrow_end=False))
    canvas.draw(node)
    monkeypatch.setattr(Node, "decompose", unexpected)
    source = canvas.render("tikz")
    assert r"\node[rectangle,anchor=center" in source
    assert f"minimum width={number(node.bounds.width)}mm" in source
    assert "Native label" in source
    assert r"\newfontfamily" in source
    assert "controls" not in source
    assert r"\newfontfamily" in canvas.latex_preamble()


def test_svg_uses_general_node_rule(font: Font, monkeypatch: pytest.MonkeyPatch) -> None:
    calls = 0
    original = Node.decompose

    def counted(node: Node) -> tuple[Drawing, ...]:
        nonlocal calls
        calls += 1
        return original(node)

    canvas = Canvas(50, 50)
    canvas.draw(Node(Text("Fallback", font), position=(20, 20)))
    monkeypatch.setattr(Node, "decompose", counted)
    output = canvas.render()
    assert "<rect" in output and "<text" in output
    assert calls == 1


@pytest.mark.parametrize(
    ("transform", "native"),
    [
        (Transform.translate(20, 20) @ Transform.rotate(30), True),
        (Transform.scale(2), False),
        (Transform.scale(2, 1), False),
        (Transform.scale(-1, 1), False),
        (Transform(1, 0, 0.5, 1, 0, 0), False),
    ],
)
def test_native_capability_respects_transform(
    font: Font, transform: Transform, native: bool
) -> None:
    node = Node(Text("P", font), shape="circle")
    canvas = Canvas(100, 100)
    canvas.draw(Drawing(node, transform=transform))
    assert (r"\node[circle,anchor=center" in canvas.render("tikz")) is native
