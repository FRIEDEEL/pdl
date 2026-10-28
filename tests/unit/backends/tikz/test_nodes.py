"""Diagram components are captured as ordinary author shapes for both adapters."""

import pytest

from pdl import Canvas, Drawing, Font, Node, Text, Transform


def test_node_is_captured_before_backend_dispatch(
    font: Font, monkeypatch: pytest.MonkeyPatch
) -> None:
    node = Node(Text("Fixed label", font), position=(30, 20))
    canvas = Canvas(100, 50)
    canvas.draw(node)

    def unexpected(node: Node) -> tuple[Drawing, ...]:
        raise AssertionError("Output must not revisit extension objects")

    monkeypatch.setattr(Node, "decompose", unexpected)
    source = canvas.render("tikz")
    assert "Fixed label" in source
    assert r"\node[rectangle" not in source
    assert r"\path" in source
    assert "<rect" in canvas.render()
    assert r"\newfontfamily" in canvas.latex_preamble()


@pytest.mark.parametrize(
    "transform",
    [
        Transform.rotate(30),
        Transform.scale(2),
        Transform.scale(2, 1),
        Transform.scale(-1, 1),
        Transform.shear(0.5),
    ],
)
def test_node_affine_placement_uses_fixed_shape_and_label(font: Font, transform: Transform) -> None:
    canvas = Canvas(100, 100)
    canvas.draw(Drawing(Node(Text("P", font), shape="circle"), transform=transform))
    source = canvas.render("tikz")
    assert r"\node[circle" not in source
    assert r"\path" in source
    assert "P" in source
    assert "<text" in canvas.render()
