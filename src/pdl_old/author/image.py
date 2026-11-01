"""Immutable PNG/JPEG image descriptions with explicit millimeter placement."""

from __future__ import annotations

from dataclasses import dataclass, field
from hashlib import sha256
from math import isfinite
from pathlib import Path as FilePath
from struct import unpack
from tempfile import gettempdir
from typing import Literal

from pdl.author.entity import Entity
from pdl.author.shapes import Path, Rectangle
from pdl.foundation.geometry.primitives import Position, point


def image_size(data: bytes) -> tuple[int, int, str]:
    """Read dimensions from PNG IHDR or JPEG frame markers without decoding pixels."""
    if data.startswith(b"\x89PNG\r\n\x1a\n") and len(data) >= 33 and data[12:16] == b"IHDR":
        width, height = unpack(">II", data[16:24])
        if width and height:
            return width, height, "png"
    if data.startswith(b"\xff\xd8"):
        offset = 2
        while offset + 3 < len(data):
            if data[offset] != 255:
                break
            while offset < len(data) and data[offset] == 255:
                offset += 1
            if offset >= len(data):
                break
            marker = data[offset]
            offset += 1
            if marker in (0xD9, 0xDA):
                break
            if marker == 0x01 or 0xD0 <= marker <= 0xD8:
                continue
            length = int.from_bytes(data[offset : offset + 2], "big")
            if length < 2 or offset + length > len(data):
                break
            if marker in (0xC0, 0xC1, 0xC2) and length >= 8:
                height, width = unpack(">HH", data[offset + 3 : offset + 7])
                if width and height:
                    return width, height, "jpeg"
            offset += length
    raise ValueError("Expected a PNG or baseline/progressive JPEG with valid dimensions.")


@dataclass(eq=False)
class Image(Entity):
    """An image captured from disk, placed inside an explicit rectangular viewport.

    Args:
        source: Local PNG or JPEG file; bytes are captured at construction.
        width: Positive viewport width in millimeters.
        height: Positive viewport height in millimeters.
        position: Lower-left viewport corner in local millimeters.
        fit: ``contain`` centers without cropping, ``cover`` centers and crops,
            ``stretch`` ignores source aspect ratio.

    SVG embeds bytes as a data URL. TikZ references a content-addressed temporary
    asset; Canvas.save copies assets next to the TeX source for portability.
    Pixel dimensions determine aspect ratio; embedded DPI and EXIF orientation
    are ignored. Paint fill/stroke do not recolor images. No remote URLs, SVG,
    PDF import, pixel decoding, or color-profile conversion is provided.
    """

    source: str | FilePath
    width: float
    height: float
    position: Position = (0, 0)
    fit: Literal["contain", "cover", "stretch"] = "contain"
    data: bytes = field(init=False, repr=False)
    pixel_width: int = field(init=False)
    pixel_height: int = field(init=False)
    format: str = field(init=False)

    def __post_init__(self) -> None:
        if not all(isfinite(v) and v > 0 for v in (self.width, self.height)):
            raise ValueError("Image dimensions must be positive and finite.")
        point(self.position)
        if self.fit not in ("contain", "cover", "stretch"):
            raise ValueError("Unknown image fit mode.")
        data = FilePath(self.source).read_bytes()
        width, height, kind = image_size(data)
        object.__setattr__(self, "data", data)
        object.__setattr__(self, "pixel_width", width)
        object.__setattr__(self, "pixel_height", height)
        object.__setattr__(self, "format", kind)

    def to_path(self) -> Path:
        """Return the rectangular viewport for geometric bounds and anchors."""
        return Rectangle(self.position, self.width, self.height).to_path()

    def content_box(self) -> tuple[float, float, float, float]:
        """Return the centered pixel placement before viewport clipping."""
        p = point(self.position)
        width, height = self.width, self.height
        if self.fit != "stretch":
            ratios = width / self.pixel_width, height / self.pixel_height
            scale = min(ratios) if self.fit == "contain" else max(ratios)
            width, height = self.pixel_width * scale, self.pixel_height * scale
        return p.x + (self.width - width) / 2, p.y + (self.height - height) / 2, width, height

    def asset(self, directory: FilePath | None = None) -> FilePath:
        """Materialize immutable bytes for TeX; the returned asset is required to compile."""
        directory = FilePath(gettempdir()) / "pdl-image-assets" if directory is None else directory
        directory.mkdir(parents=True, exist_ok=True)
        destination = directory / f"pdl-{sha256(self.data).hexdigest()}.{self.format}"
        if not destination.exists() or destination.read_bytes() != self.data:
            destination.write_bytes(self.data)
        return destination.resolve()
