"""Convenient drawing constructors returning the same thin Entity type."""

from pathlib import Path as FilePath
from typing import Literal

from pdl.author.entity.base import Entity
from pdl.author.entity.capture import Composite
from pdl.author.entity.group import Group
from pdl.author.geometry import shapes
from pdl.author.geometry.frame import Frame
from pdl.author.geometry.image import Image as ImageGeometry
from pdl.author.geometry.path import Path as PathGeometry
from pdl.author.geometry.point import Position, as_point
from pdl.author.geometry.tex import TeX as TeXGeometry
from pdl.author.geometry.text import Text as TextGeometry
from pdl.author.style import BLACK, Font, FontStack, Style
from pdl.author.transform.affine import AffineTransform
from pdl.author.util.tex import TeXConfig

TEXT_STYLE = Style(stroke=None, fill=BLACK)


def Circle(center: Position = (0, 0), radius: float = 1, *, style: Style | None = None) -> Entity:
    return Entity(shapes.Circle(center, radius), style=style)


def Line(start: Position, end: Position, *, style: Style | None = None) -> Entity:
    return Entity(shapes.Line(start, end), style=style)


def Polyline(points: tuple[Position, ...], *, style: Style | None = None) -> Entity:
    return Entity(shapes.Polyline(points), style=style)


def Polygon(points: tuple[Position, ...], *, style: Style | None = None) -> Entity:
    return Entity(shapes.Polygon(points), style=style)


def Rectangle(
    origin: Position, width: float, height: float, *, style: Style | None = None
) -> Entity:
    return Entity(shapes.Rectangle(origin, width, height), style=style)


def Arc(
    center: Position,
    radius_x: float,
    radius_y: float,
    start_angle: float,
    sweep_angle: float,
    rotation: float = 0,
    *,
    style: Style | None = None,
) -> Entity:
    return Entity(
        shapes.Arc(center, radius_x, radius_y, start_angle, sweep_angle, rotation), style=style
    )


def Path(geometry: PathGeometry | None = None, *, style: Style | None = None) -> Entity:
    return Entity(PathGeometry() if geometry is None else geometry, style=style)


def Text(
    text: str,
    font: Font | FontStack | None = None,
    position: Position = (0, 0),
    size: float = 12,
    align: Literal["left", "center", "right"] = "left",
    line_spacing: float = 1.25,
    *,
    style: Style | None = None,
) -> Entity:
    return Entity(
        TextGeometry(text, font, position, size, align, line_spacing),
        style=style,
        default_style=TEXT_STYLE,
    )


def TeX(
    source: str,
    position: Position = (0, 0),
    size: float = 12,
    config: TeXConfig | None = None,
    *,
    style: Style | None = None,
) -> Entity:
    return Entity(
        TeXGeometry(source, position, size, config), style=style, default_style=TEXT_STYLE
    )


def Image(
    source: str | FilePath,
    width: float,
    height: float,
    position: Position = (0, 0),
    fit: Literal["contain", "cover", "stretch"] = "contain",
    *,
    style: Style | None = None,
) -> Entity:
    return Entity(ImageGeometry(source, width, height, position, fit), style=style)


def frame_axes(frame: Frame, *, length: float = 10, style: Style | None = None) -> Group:
    p = as_point(frame.origin)
    x, y = frame.point((length, 0)), frame.point((0, length))
    return Group(Line(p, x), Line(p, y), style=style, reference=p)


def as_entity(
    geometry: object, style: Style | None = None, transform: AffineTransform = AffineTransform()
) -> Entity:
    """Embed a description or detach an existing Entity for independent ownership."""
    if isinstance(geometry, Entity):
        result = geometry.copy()
        if style is not None:
            result.set_style(style)
    elif isinstance(geometry, Composite):
        result = Group(*geometry.decompose(), style=style)
    else:
        result = Entity(geometry, style=style)
    return result if transform == AffineTransform() else result.apply_transform(transform)
