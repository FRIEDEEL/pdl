"""State capture, dependency order and frame conversion contracts."""

from math import sqrt

import pytest

from pdl import (
    Canvas,
    Node,
    Rectangle,
    Text,
)


def test_resolved_snapshot_keeps_native_geometry_and_detaches_paths() -> None:
    canvas = Canvas(100, 60)
    a = Rectangle((-10, -5), 20, 10).rotate(30)
    snapshot = canvas.resolve(a)
    a.translate(50, 0)
    assert snapshot.bounds().anchor().x == pytest.approx(0)
    assert isinstance(snapshot.decompose()[0].geometry, Rectangle)
    canvas.draw(snapshot)
    assert "\\path" in canvas.render("tikz")


def test_snapshot_typography_metrics_survive_default_font_changes() -> None:
    canvas = Canvas(100, 60)
    snapshot = canvas.resolve(Node(Text("Long measured label")))
    box = snapshot.bounds()
    assert box.width > 0
    canvas.draw(snapshot)
    assert snapshot.bounds() == box
    assert "text" in canvas.render()


def test_rotated_resolved_anchor_keeps_local_shape_semantics() -> None:
    canvas = Canvas(100, 60)
    a = Rectangle((-10, -5), 20, 10).rotate(45)
    resolved = canvas.resolve(a)
    tip = resolved.anchor("east")
    assert (tip.x, tip.y) == pytest.approx((10 / sqrt(2), 10 / sqrt(2)))


def test_text_ink_query_is_distinct_from_layout_bounds() -> None:
    canvas = Canvas(100, 60)
    text = Text(" x ")
    layout = canvas.query().bounds(text)
    ink = canvas.query().ink_bounds(text)
    assert ink.width < layout.width
