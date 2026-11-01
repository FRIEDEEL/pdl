"""State capture, dependency order and frame conversion contracts."""

from math import sqrt

import pytest

from pdl import (
    Canvas,
    Node,
    Rectangle,
    Text,
)


def test_snapshot_keeps_native_geometry_and_detaches_paths() -> None:
    canvas = Canvas(100, 60)
    a = Rectangle((-10, -5), 20, 10).rotate(30)
    snapshot = canvas.snapshot(a)
    a.translate(50, 0)
    assert canvas.bounds(snapshot).anchor().x == pytest.approx(0)
    assert isinstance(snapshot.geometry, Rectangle)
    canvas.draw(snapshot)
    assert "\\path" in canvas.render("tikz")


def test_snapshot_typography_metrics_survive_default_font_changes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    canvas = Canvas(100, 60)
    snapshot = canvas.snapshot(Node(Text("Long measured label")))
    box = canvas.bounds(snapshot)
    assert box.width > 0

    def unavailable() -> tuple[()]:
        raise AssertionError("Captured text must not rediscover fonts")

    monkeypatch.setattr("pdl.foundation.typography.config.default_fonts", unavailable)
    canvas.draw(snapshot)
    assert canvas.bounds(snapshot) == box
    assert "text" in canvas.render()


def test_rotated_snapshot_anchor_keeps_local_shape_semantics() -> None:
    canvas = Canvas(100, 60)
    a = Rectangle((-10, -5), 20, 10).rotate(45)
    snapshot = canvas.snapshot(a)
    tip = snapshot.anchor("east")
    assert (tip.x, tip.y) == pytest.approx((10 / sqrt(2), 10 / sqrt(2)))


def test_text_ink_query_is_distinct_from_layout_bounds() -> None:
    canvas = Canvas(100, 60)
    text = Text(" x ")
    layout = canvas.query().bounds(text)
    ink = canvas.query().ink_bounds(text)
    assert ink.width < layout.width
