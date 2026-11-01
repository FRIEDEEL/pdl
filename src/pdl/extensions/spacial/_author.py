"""Small construction helpers producing ordinary Author Entities."""

from pdl.author.entity.base import Entity
from pdl.author.entity.capture import Composite
from pdl.author.entity.group import Group
from pdl.author.style import Style
from pdl.author.transform.affine import AffineTransform


def make_entity(
    geometry: object, style: Style | None = None, transform: AffineTransform = AffineTransform()
) -> Entity:
    if isinstance(geometry, Entity):
        result = geometry.copy()
        if style is not None:
            result.set_style(style)
    elif isinstance(geometry, Composite):
        result = Group(*geometry.decompose(), style=style)
    else:
        result = Entity(geometry, style=style)
    return result.apply_transform(transform)


def make_group(children: tuple[Entity, ...]) -> Group:
    return Group(*children)
