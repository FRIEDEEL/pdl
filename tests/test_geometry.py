"""Public geometry behavior and numerical regression coverage."""

from math import hypot

import pytest

from pdl import Arc, Circle, Line, Path, Point, Polygon, Rectangle
from pdl.geometry import Close, Cubic, Move, Segment


def test_path_subpaths_and_snapshot() -> None:
    path = Path().move_to((0, 0)).line_to((2, 0)).close().line_to((1, 1))
    snapshot = path.to_path()
    path.move_to((4, 4))
    assert snapshot.commands[-1] == Segment(Point(1, 1))
    assert isinstance(snapshot.commands[2], Close)
    assert len(path.commands) == len(snapshot.commands) + 1


@pytest.mark.parametrize("operation", ["line", "quadratic", "cubic", "close"])
def test_path_requires_start(operation: str) -> None:
    with pytest.raises(ValueError):
        match operation:
            case "line":
                Path().line_to((0, 0))
            case "quadratic":
                Path().quadratic_to((1, 1), (0, 0))
            case "cubic":
                Path().cubic_to((1, 1), (2, 2), (0, 0))
            case _:
                Path().close()


def test_shapes_lower_to_closed_paths() -> None:
    for shape in (
        Circle((0, 0), 2),
        Rectangle((1, 2), 3, 4),
        Polygon(((0, 0), (2, 0), (1, 1))),
    ):
        assert isinstance(shape.to_path().commands[-1], Close)
    assert Rectangle((1, 2), 3, 4).to_path().commands[2] == Segment(Point(4, 6))


@pytest.mark.parametrize("large", [False, True])
@pytest.mark.parametrize("sweep", [False, True])
def test_svg_arc_flags_preserve_endpoints(large: bool, sweep: bool) -> None:
    arc = Arc.from_svg(
        (1, 2),
        (7, 5),
        radius_x=8,
        radius_y=4,
        rotation=31,
        large_arc=large,
        sweep=sweep,
    )
    assert isinstance(arc, Arc)
    start, end = arc.at(arc.start_angle), arc.at(arc.start_angle + arc.sweep_angle)
    assert (start.x, start.y) == pytest.approx((1, 2))
    assert (end.x, end.y) == pytest.approx((7, 5))
    assert (abs(arc.sweep_angle) > 180) == large
    assert (arc.sweep_angle > 0) == sweep


def test_svg_arc_radius_correction_and_degeneracy() -> None:
    arc = Arc.from_svg((0, 0), (10, 0), radius_x=1, radius_y=1)
    assert isinstance(arc, Arc)
    assert arc.radius_x == pytest.approx(5)
    assert isinstance(Arc.from_svg((0, 0), (1, 1), radius_x=0, radius_y=1), Line)
    omitted = Arc.from_svg((1, 1), (1, 1), radius_x=1, radius_y=1)
    assert isinstance(omitted, Path)
    assert omitted.commands == (Move(Point(1, 1)),)


def test_tikz_arc_starts_at_requested_point() -> None:
    arc = Arc.from_tikz((4, 5), radius=3, start_angle=45, end_angle=-90)
    start = arc.at(arc.start_angle)
    assert (start.x, start.y) == pytest.approx((4, 5))
    assert arc.sweep_angle == -135


def test_cubic_arc_fallback_error() -> None:
    arc = Arc((0, 0), 1, 1, 0, 360)
    previous = arc.at(0)
    for command in arc.to_path().commands[1:]:
        assert isinstance(command, Cubic)
        for t in (0.1, 0.25, 0.5, 0.75, 0.9):
            u = 1 - t
            x = (
                u**3 * previous.x
                + 3 * u * u * t * command.control1.x
                + 3 * u * t * t * command.control2.x
                + t**3 * command.end.x
            )
            y = (
                u**3 * previous.y
                + 3 * u * u * t * command.control1.y
                + 3 * u * t * t * command.control2.y
                + t**3 * command.end.y
            )
            assert abs(hypot(x, y) - 1) < 5e-6
        previous = command.end


def test_invalid_geometry() -> None:
    with pytest.raises(ValueError):
        Point(float("nan"), 0)
    with pytest.raises(ValueError):
        Circle((0, 0), -1)
    with pytest.raises(ValueError):
        Rectangle((0, 0), -1, 3)
    with pytest.raises(ValueError):
        Arc((0, 0), 1, 1, 0, 361)
