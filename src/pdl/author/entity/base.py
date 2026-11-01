"""Minimal Entity state with explicit geometry sharing and type-level style defaults."""

from typing import ClassVar, Self

from pdl.author.style.style import Style


class Entity[GeometryT]:
    """A drawing instance holding its geometry directly and its own optional style.

    The geometry argument is stored by reference, never copied or converted.
    Passing one mutable description to multiple Entities deliberately shares
    that description: later geometry edits are visible to each holder. Concrete
    drawing constructors should normally create their own geometry. Callers who
    need independent descriptions must copy the geometry explicitly beforehand.

    GeometryT preserves the concrete geometry type without requiring a common
    Geometry base or path interface. This base does not inspect its geometry,
    compute anchors, or decide transformation behavior. Group relationships,
    transformation storage, copying, submission, and output are not implemented
    in this checkpoint. Entity identity is independent of geometry identity.

    ``style`` records only the explicit instance value. When it is None,
    ``effective_style`` reads the current class-level ``default_style`` without
    writing it back. Subclasses may override that default independently; changing
    a class default affects existing instances without explicit paint. Group
    fallback will be implemented with the Group ownership rules later.

    Args:
        geometry: Description to hold directly, without implicit ownership checks.
        style: Explicit style, or None to use the Entity type's current default.
    """

    default_style: ClassVar[Style] = Style()

    def __init__(self, geometry: GeometryT, *, style: Style | None = None) -> None:
        self._geometry = geometry
        self._style = style

    @property
    def geometry(self) -> GeometryT:
        """Return the held description itself, not a copy or transformed result."""
        return self._geometry

    @property
    def style(self) -> Style | None:
        """Return explicit instance paint, retaining None for an unset style."""
        return self._style

    @property
    def effective_style(self) -> Style:
        """Read explicit paint or the current type default without modifying state.

        Returns:
            The explicit Style object, or the current class default. No field-wise
            merging or Group inheritance is performed by this base yet.
        """
        return self._style if self._style is not None else type(self).default_style

    def set_style(self, style: Style) -> Self:
        """Set only this instance's explicit Style and return this instance.

        Args:
            style: Complete immutable style value to retain directly. Resetting
                with None is not part of this checkpoint's API.

        Returns:
            This modified Entity. Neither its geometry nor any other Entity is
            modified, including Entities sharing the same geometry.
        """
        self._style = style
        return self
