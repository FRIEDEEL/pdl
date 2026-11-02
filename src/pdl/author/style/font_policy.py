"""Task-local explicit font selection shared by measurement and output."""

from collections.abc import Callable, Generator
from contextlib import contextmanager
from contextvars import ContextVar

from pdl.author.style.font import Font

type FontPolicy = tuple[Font, ...] | Callable[[], tuple[Font, ...]]

font_policy: ContextVar[FontPolicy] = ContextVar("pdl_fonts", default=())


@contextmanager
def font_context(fonts: FontPolicy) -> Generator[None, None, None]:
    """Use task-local defaults for measurement and rendering together."""
    token = font_policy.set(fonts)
    try:
        yield
    finally:
        font_policy.reset(token)
