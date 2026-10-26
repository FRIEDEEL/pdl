"""Shared numeric serialization for vector backends."""


def number(value: float) -> str:
    """Serialize finite drawing coordinates with stable precision."""
    return format(0.0 if value == 0 else value, ".12g")
