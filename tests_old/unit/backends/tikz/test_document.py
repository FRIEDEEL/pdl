"""Backend semantics, fallback and real TikZ compilation."""

from pdl import Arc, Canvas, Path


def test_quadratic_is_exactly_elevated_for_tikz() -> None:
    canvas = Canvas(10, 10)
    canvas.draw(Path().move_to((0, 0)).quadratic_to((3, 6), (6, 0)))
    assert "Q 3 6 6 0" in canvas.render()
    assert "controls (2,4) and (4,4) .. (6,0)" in canvas.render("tikz")


def test_native_arc_and_rotated_fallback() -> None:
    canvas = Canvas(30, 30)
    canvas.draw(Arc((10, 10), 4, 2, 0, 360))
    assert canvas.render().count(" A ") == 2
    assert "arc[" in canvas.render("tikz")
    canvas.draw(Arc((10, 10), 4, 2, 0, 90, rotation=30))
    assert "controls" in canvas.render("tikz")
