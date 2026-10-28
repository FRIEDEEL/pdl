"""Native capability selection precedes general authoring decomposition."""

from pdl import Drawing, Group, Rectangle, Style, Transform
from pdl.backends.traversal import prepare


class NativeOnly:
    def decompose(self) -> tuple[Drawing, ...]:
        raise AssertionError("Supported objects must reach the backend intact.")


def test_supported_object_keeps_identity_and_inherited_placement() -> None:
    native = NativeOnly()
    paint = Style(line_width=2)
    placement = Transform.translate(10, 20)
    parent = Group((Drawing(native),), placement)
    result = tuple(
        prepare((Drawing(parent, paint),), lambda drawing: isinstance(drawing.geometry, NativeOnly))
    )
    assert len(result) == 1
    assert result[0].geometry is native
    assert result[0].transform == placement
    assert result[0].style is paint


def test_unsupported_object_falls_back_in_original_order() -> None:
    first, second = Rectangle((0, 0), 1, 1), Rectangle((3, 0), 1, 1)
    group = Group((Drawing(first), Drawing(second)))
    result = tuple(prepare((Drawing(group),), lambda _: False))
    assert [
        drawing.geometry.origin for drawing in result if isinstance(drawing.geometry, Rectangle)
    ] == [(0, 0), (3, 0)]
