"""Basic drawing stays convenient while advanced APIs require explicit imports."""

from importlib import import_module
from xml.etree import ElementTree as ET

import pytest

from pdl import Canvas, Color, Entity, Gather, Group, Style, circle, rectangle
from pdl.author.geometry import Circle, Path
from pdl.extensions.spatial import OrthographicCamera, Scene3D, regular_polyhedron


@pytest.mark.parametrize("package", ["pdl", "pdl.author"])
def test_advanced_objects_are_not_root_authoring_shortcuts(package: str) -> None:
    module = import_module(package)
    for name in ("Point", "PathGeometry", "AffineTransform", "Font", "Layer", "Scene3D", "Node"):
        with pytest.raises(AttributeError):
            getattr(module, name)


def test_basic_drawing_needs_no_geometry_or_extension_imports() -> None:
    assembly = Group(circle((10, 10), 3), rectangle((20, 5), 8, 8))
    assembly.set_style(Style(stroke=None, fill=Color(0.2, 0.5, 0.8)))
    Gather(assembly).translate(5, 0)
    output = ET.fromstring(Canvas(50, 30).add(assembly).render())
    assert len(output[0]) == 2
    assert isinstance(assembly.members[0], Entity)


def test_explicit_geometry_and_spatial_entrypoints_work_with_core_entities() -> None:
    description = Circle((5, 5), 2)
    outlined = Entity(Path().extend(description))
    projection = Scene3D(
        (regular_polyhedron("cube", radius=3),), camera=OrthographicCamera(30, 25)
    ).project()
    canvas = Canvas(50, 30).add(outlined, projection)
    ET.fromstring(canvas.render())
    assert "tikzpicture" in canvas.render("tikz")
