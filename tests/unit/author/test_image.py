"""Image capture, viewport fitting, and standalone SVG/TikZ resources."""

from pathlib import Path
from xml.etree import ElementTree as ET

import pytest

from pdl import Canvas, Drawing, Image, Transform
from pdl.author.image import image_size

ASSET = Path(__file__).parents[3] / "examples/tutorial/media/quadrants.png"


def test_image_fits_and_captures_file_bytes(tmp_path: Path) -> None:
    source = tmp_path / "source.png"
    data = ASSET.read_bytes()
    source.write_bytes(data)
    image = Image(source, 20, 20)
    assert image.content_box() == (0, 5, 20, 10)
    assert Image(source, 20, 20, fit="cover").content_box() == (-10, 0, 40, 20)
    assert Image(source, 20, 20, fit="stretch").content_box() == (0, 0, 20, 20)
    source.unlink()
    canvas = Canvas(80, 60)
    canvas.draw(Drawing(image, transform=Transform.shear(0.5)))
    assert canvas.bounds(canvas.drawings[0]).right == 30
    root = ET.fromstring(canvas.render())
    embedded = root.find(".//{http://www.w3.org/2000/svg}image")
    assert embedded is not None
    assert embedded.attrib["href"].startswith("data:image/png;base64,")
    canvas.save(tmp_path / "drawing.tex", backend="tikz", tikz_mode="tex")
    assets = list((tmp_path / "drawing-assets").iterdir())
    assert len(assets) == 1
    assert assets[0].read_bytes() == data
    assert "drawing-assets/" in (tmp_path / "drawing.tex").read_text()
    assert str(tmp_path) not in (tmp_path / "drawing.tex").read_text()


def test_reject_unsupported_images_and_invalid_dimensions(tmp_path: Path) -> None:
    bad = tmp_path / "bad.svg"
    bad.write_text("<svg/>")
    with pytest.raises(ValueError, match="PNG"):
        Image(bad, 20, 20)
    with pytest.raises(ValueError, match="dimensions"):
        Image(ASSET, 0, 20)
    for data in (b"\xff\xd8", b"\xff\xd8\xff\xc0\x00\x01", b""):
        with pytest.raises(ValueError):
            image_size(data)


def test_baseline_and_progressive_jpeg_dimensions() -> None:
    for marker in (0xC0, 0xC2):
        data = bytes((255, 216, 255, marker, 0, 8, 8, 0, 20, 0, 40, 3))
        assert image_size(data) == (40, 20, "jpeg")


def test_tikz_save_keeps_font_policy_during_asset_discovery(tmp_path: Path) -> None:
    from pdl import Text
    from pdl.extensions.diagrams.debug import debug_overlay

    canvas = Canvas(100, 60)
    label = Text("Overlay")
    canvas.draw(label)
    canvas.draw(debug_overlay(label))
    canvas.save(tmp_path / "overlay.tex", backend="tikz", tikz_mode="tex")
    assert (tmp_path / "overlay.tex").is_file()
