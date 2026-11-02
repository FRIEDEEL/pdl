"""Path construction, subpath continuity, and independent snapshots."""

from dataclasses import FrozenInstanceError

import pytest

from pdl.author.geometry.path import Close, Cubic, Move, Path, Quadratic, Segment
from pdl.author.geometry.point import Point


def test_empty_path() -> None:
    path = Path()
    assert path.commands == ()
    assert path.current_point is None


def test_absolute_lines_and_beziers_chain() -> None:
    path = Path()
    result = (
        path.move_to((1, 2))
        .line_to(Point(3, 4))
        .quadratic_to((5, 6), (7, 8))
        .cubic_to((9, 10), (11, 12), (13, 14))
    )
    assert result is path
    assert path.commands == (
        Move(Point(1, 2)),
        Segment(Point(3, 4)),
        Quadratic(Point(5, 6), Point(7, 8)),
        Cubic(Point(9, 10), Point(11, 12), Point(13, 14)),
    )
    assert path.current_point == Point(13, 14)


@pytest.mark.parametrize("operation", ["line", "quadratic", "cubic", "close"])
def test_operations_require_a_started_subpath(operation: str) -> None:
    path = Path()
    with pytest.raises(ValueError, match="move_to"):
        match operation:
            case "line":
                path.line_to((1, 1))
            case "quadratic":
                path.quadratic_to((1, 2), (3, 4))
            case "cubic":
                path.cubic_to((1, 2), (3, 4), (5, 6))
            case _:
                path.close()
    assert path.commands == ()
    assert path.current_point is None


def test_close_and_multiple_subpaths_keep_their_own_start() -> None:
    path = Path().move_to((1, 2)).line_to((3, 4)).close()
    assert path.current_point == Point(1, 2)
    path.line_to((5, 6)).move_to((10, 20)).line_to((30, 40)).close()
    assert path.current_point == Point(10, 20)
    assert path.commands == (
        Move(Point(1, 2)),
        Segment(Point(3, 4)),
        Close(),
        Segment(Point(5, 6)),
        Move(Point(10, 20)),
        Segment(Point(30, 40)),
        Close(),
    )


def test_command_snapshots_are_immutable_and_do_not_follow_edits() -> None:
    path = Path().move_to((1, 2))
    commands = path.commands
    path.line_to((3, 4))
    assert commands == (Move(Point(1, 2)),)
    with pytest.raises(FrozenInstanceError):
        setattr(commands[0], "end", Point(5, 6))


def test_copy_preserves_cursor_and_can_be_edited_independently() -> None:
    path = Path().move_to((1, 2)).line_to((3, 4))
    duplicate = path.copy().close()
    assert duplicate.current_point == Point(1, 2)
    assert path.current_point == Point(3, 4)
    path.line_to((5, 6))
    duplicate.line_to((7, 8))
    assert path.commands[-1] == Segment(Point(5, 6))
    assert duplicate.commands[-1] == Segment(Point(7, 8))


def test_extend_keeps_subpaths_and_is_independent_of_the_source() -> None:
    first = Path().move_to((0, 0)).line_to((1, 0))
    second = Path().move_to((10, 20)).line_to((30, 40))
    assert first.extend(second) is first
    first.close()
    assert first.current_point == Point(10, 20)
    second.line_to((50, 60))
    assert first.commands == (
        Move(Point(0, 0)),
        Segment(Point(1, 0)),
        Move(Point(10, 20)),
        Segment(Point(30, 40)),
        Close(),
    )


def test_extend_empty_path_and_self_extension() -> None:
    path = Path().move_to((1, 2)).line_to((3, 4))
    before = path.commands
    path.extend(Path())
    assert path.commands == before
    assert path.current_point == Point(3, 4)
    path.extend(path)
    assert path.commands == before + before
    path.close()
    assert path.current_point == Point(1, 2)


@pytest.mark.parametrize("operation", ["move", "line", "quadratic", "cubic"])
def test_invalid_coordinates_do_not_partially_change_the_builder(operation: str) -> None:
    path = Path().move_to((1, 2)).line_to((3, 4))
    before = path.commands
    invalid = (float("nan"), 5)
    with pytest.raises(ValueError, match="finite"):
        match operation:
            case "move":
                path.move_to(invalid)
            case "line":
                path.line_to(invalid)
            case "quadratic":
                path.quadratic_to(invalid, (10, 20))
            case _:
                path.cubic_to((10, 20), invalid, (30, 40))
    assert path.commands == before
    assert path.current_point == Point(3, 4)
