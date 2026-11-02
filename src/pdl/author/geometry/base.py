"""Nominal membership for geometric descriptions, independent of capabilities."""


class Geometry:
    """Identify a geometric description accepted by Entity and geometry dispatch.

    Membership defines no shared data or operations. Subclasses provide only
    their meaningful capabilities; path conversion, bounds queries, and
    transforms are not required by this base. In particular, inheriting Geometry
    does not guarantee that a backend can render the description.
    """
