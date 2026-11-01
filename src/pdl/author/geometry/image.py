"""Captured image bytes and current world-coordinate viewport corners."""

from __future__ import annotations

from dataclasses import dataclass, field
from hashlib import sha256
from math import isfinite
from pathlib import Path as FilePath
from tempfile import gettempdir
from typing import Literal

from pdl.author.geometry.path import Path
from pdl.author.geometry.point import Point, Position
from pdl.author.geometry.point import as_point as point
from pdl.author.geometry.shapes import Polygon
from pdl.author.transform.affine import AffineTransform
from pdl.author.util.images import image_size


@dataclass(eq=False)
class Image:
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
    corners: tuple[Point, Point, Point, Point] = field(init=False)
    data: bytes = field(init=False, repr=False)
    pixel_width: int = field(init=False)
    pixel_height: int = field(init=False)
    format: str = field(init=False)

    def __post_init__(self) -> None:
        if not all(isfinite(v) and v > 0 for v in (self.width, self.height)):
            raise ValueError("Image dimensions must be positive and finite.")
        p = point(self.position)
        self.corners = (
            p,
            Point(p.x + self.width, p.y),
            Point(p.x + self.width, p.y + self.height),
            Point(p.x, p.y + self.height),
        )
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
        return Polygon(self.corners).to_path()

    def content_box(self) -> tuple[float, float, float, float]:
        """Return the centered pixel placement before viewport clipping."""
        width, height = self.width, self.height
        if self.fit != "stretch":
            ratios = width / self.pixel_width, height / self.pixel_height
            scale = min(ratios) if self.fit == "contain" else max(ratios)
            width, height = self.pixel_width * scale, self.pixel_height * scale
        return (self.width - width) / 2, (self.height - height) / 2, width, height

    def asset(self, directory: FilePath | None = None) -> FilePath:
        """Materialize immutable bytes for TeX; the returned asset is required to compile."""
        directory = FilePath(gettempdir()) / "pdl-image-assets" if directory is None else directory
        directory.mkdir(parents=True, exist_ok=True)
        destination = directory / f"pdl-{sha256(self.data).hexdigest()}.{self.format}"
        if not destination.exists() or destination.read_bytes() != self.data:
            destination.write_bytes(self.data)
        return destination.resolve()

    @property
    def mapping(self) -> AffineTransform:
        """Derive pixel-viewport placement from current corner coordinates."""
        p, q, _, v = self.corners
        return AffineTransform(
            (q.x - p.x) / self.width,
            (q.y - p.y) / self.width,
            (v.x - p.x) / self.height,
            (v.y - p.y) / self.height,
            p.x,
            p.y,
        )
