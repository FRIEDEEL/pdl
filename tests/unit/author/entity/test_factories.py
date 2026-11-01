"""Drawing factories preserve direct Entity construction and optional paint."""

from pdl.author.entity.base import Entity
from pdl.author.entity.factories import Circle, Text
from pdl.author.geometry.point import Point
from pdl.author.geometry.shapes import Circle as CircleGeometry
from pdl.author.style.color import BLACK


def test_circle_factory_returns_thin_entity() -> None:
    entity = Circle((3, 4), 2)
    assert type(entity) is Entity
    assert isinstance(entity.geometry, CircleGeometry)
    assert entity.style is None
    assert entity.move_to((5, 6)) is entity
    assert entity.reference == Point(5, 6)


def test_text_default_fill_survives_representation_change() -> None:
    entity = Text("A")
    assert entity.style is None
    assert entity.effective_style.fill == BLACK
    assert entity.effective_style.stroke is None
    entity.scale(2, 1)
    assert entity.style is None
    assert entity.effective_style.fill == BLACK
    assert entity.effective_style.stroke is None
