"""Convenient drawing constructors returning the same thin Entity type."""

from pathlib import Path as FilePath
from typing import Literal

from pdl.author.entity.base import Entity
from pdl.author.entity.capture import Composite
from pdl.author.entity.frames import FrameAxes
from pdl.author.entity.group import Group
from pdl.author.geometry import shapes
from pdl.author.geometry.frame import Frame
from pdl.author.geometry.image import Image as ImageGeometry
from pdl.author.geometry.path import Path as PathGeometry
from pdl.author.geometry.point import Position
from pdl.author.geometry.tex import TeX as TeXGeometry
from pdl.author.geometry.text import Text as TextGeometry
from pdl.author.style import Font, FontStack, Style
from pdl.author.transform.affine import AffineTransform
from pdl.author.util.tex import TeXConfig


def Circle(center: Position = (0, 0), radius: float = 1, *, style: Style | None = None) -> Entity:
    """Create a circle Entity in world millimeters, referenced at its center.

    The result is a thin Entity. An omitted style stays None and uses parent or
    role defaults when queried/submitted. Coordinates are current world values.
    Geometry-changing operations edit the Entity immediately; Canvas captures
    an independent state on submission.
    """
    return Entity(shapes.Circle(center, radius), style=style)


def Line(start: Position, end: Position, *, style: Style | None = None) -> Entity:
    """Create a segment Entity, referenced at its first endpoint.

    The result is a thin Entity. An omitted style stays None and uses parent or
    role defaults when queried/submitted. Coordinates are current world values.
    Geometry-changing operations edit the Entity immediately; Canvas captures
    an independent state on submission.
    """
    return Entity(shapes.Line(start, end), style=style)


def Polyline(points: tuple[Position, ...], *, style: Style | None = None) -> Entity:
    """Create an open chain Entity from world positions in millimeters.

    The result is a thin Entity. An omitted style stays None and uses parent or
    role defaults when queried/submitted. Coordinates are current world values.
    Geometry-changing operations edit the Entity immediately; Canvas captures
    an independent state on submission.
    """
    return Entity(shapes.Polyline(points), style=style)


def Polygon(points: tuple[Position, ...], *, style: Style | None = None) -> Entity:
    """Create a closed polygon Entity from world positions in millimeters.

    The result is a thin Entity. An omitted style stays None and uses parent or
    role defaults when queried/submitted. Coordinates are current world values.
    Geometry-changing operations edit the Entity immediately; Canvas captures
    an independent state on submission.
    """
    return Entity(shapes.Polygon(points), style=style)


def Rectangle(
    origin: Position, width: float, height: float, *, style: Style | None = None
) -> Entity:
    """Create a rectangle Entity, referenced at its lower-left origin.

    The result is a thin Entity. An omitted style stays None and uses parent or
    role defaults when queried/submitted. Coordinates are current world values.
    Geometry-changing operations edit the Entity immediately; Canvas captures
    an independent state on submission.
    """
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
    """Create an elliptical arc Entity using signed degree angles.

    The result is a thin Entity. An omitted style stays None and uses parent or
    role defaults when queried/submitted. Coordinates are current world values.
    Geometry-changing operations edit the Entity immediately; Canvas captures
    an independent state on submission.
    """
    return Entity(
        shapes.Arc(center, radius_x, radius_y, start_angle, sweep_angle, rotation), style=style
    )


def Path(geometry: PathGeometry | None = None, *, style: Style | None = None) -> Entity:
    """Create an Entity directly holding a path builder, without copying it.

    The result is a thin Entity. An omitted style stays None and uses parent or
    role defaults when queried/submitted. Coordinates are current world values.
    Geometry-changing operations edit the Entity immediately; Canvas captures
    an independent state on submission.
    """
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
    """Create literal text referenced at its baseline; size uses TeX points.

    The result is a thin Entity. An omitted style stays None and uses parent or
    role defaults when queried/submitted. Coordinates are current world values.
    Geometry-changing operations edit the Entity immediately; Canvas captures
    an independent state on submission.
    """
    return Entity(
        TextGeometry(text, font, position, size, align, line_spacing),
        style=style,
    )


def TeX(
    source: str,
    position: Position = (0, 0),
    size: float = 12,
    config: TeXConfig | None = None,
    *,
    style: Style | None = None,
) -> Entity:
    """Create native LaTeX referenced at its baseline; size uses TeX points.

    The result is a thin Entity. An omitted style stays None and uses parent or
    role defaults when queried/submitted. Coordinates are current world values.
    Geometry-changing operations edit the Entity immediately; Canvas captures
    an independent state on submission.
    """
    return Entity(TeXGeometry(source, position, size, config), style=style)


def Image(
    source: str | FilePath,
    width: float,
    height: float,
    position: Position = (0, 0),
    fit: Literal["contain", "cover", "stretch"] = "contain",
    *,
    style: Style | None = None,
) -> Entity:
    """Create an image Entity with captured pixels and a millimeter viewport.

    The result is a thin Entity. An omitted style stays None and uses parent or
    role defaults when queried/submitted. Coordinates are current world values.
    Geometry-changing operations edit the Entity immediately; Canvas captures
    an independent state on submission.
    """
    return Entity(ImageGeometry(source, width, height, position, fit), style=style)


def frame_axes(
    frame: Frame,
    *,
    length: float = 10,
    origin_radius: float = 0.5,
    style: Style | None = None,
    x_style: Style | None = None,
    y_style: Style | None = None,
    origin_style: Style | None = None,
) -> FrameAxes:
    """Create explicit drawable axes; ordinary objects have no implicit frame."""
    return FrameAxes(
        frame,
        length=length,
        origin_radius=origin_radius,
        style=style,
        x_style=x_style,
        y_style=y_style,
        origin_style=origin_style,
    )


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
