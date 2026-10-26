"""Renderer-level font discovery and document configuration."""

from __future__ import annotations

import shutil
import subprocess
from collections.abc import Generator
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from pdl.typography.plain import Font, font_context
from pdl.typography.tex import TeXConfig


@dataclass(frozen=True)
class RendererConfig:
    """Upper-level font candidates and optional shared LaTeX environment.

    Font strings are file paths, TeX-discoverable filenames, or fontconfig
    family names. A Text.font override takes precedence over these defaults.
    Native SVG text references the discovered family; fonts must be installed
    on the viewing machine. Backend font metrics may differ slightly.
    """

    fonts: tuple[Font | str, ...] = ()
    tex: TeXConfig | None = None

    def resolve_fonts(self) -> tuple[Font, ...]:
        return tuple(font if isinstance(font, Font) else resolve_font(font) for font in self.fonts)


@lru_cache(maxsize=64)
def resolve_font(request: str) -> Font:
    """Resolve a filename or family once at the renderer boundary."""
    if Path(request).is_file():
        return Font(Path(request).resolve())
    if Path(request).suffix.lower() in (".ttf", ".otf", ".ttc"):
        executable = shutil.which("kpsewhich")
        if executable:
            result = subprocess.run(
                [executable, request], capture_output=True, text=True, timeout=15, check=False
            )
            if result.stdout.strip() and Path(result.stdout.strip()).is_file():
                return Font(result.stdout.strip())
    executable = shutil.which("fc-match")
    if executable:
        result = subprocess.run(
            [executable, "-f", "%{file}\\n%{family}", request],
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )
        lines = result.stdout.splitlines()
        if len(lines) >= 2 and Path(lines[0]).is_file():
            families = [family.casefold() for family in lines[1].split(",")]
            if request.casefold() in families or request in ("sans-serif", "serif", "monospace"):
                return Font(lines[0])
    raise FileNotFoundError(f"Cannot resolve font {request!r}; provide an explicit font file.")


_current: ContextVar[RendererConfig] = ContextVar("pdl_renderer", default=RendererConfig())


def current_renderer() -> RendererConfig:
    return _current.get()


@contextmanager
def rendering(config: RendererConfig) -> Generator[None, None, None]:
    """Resolve fonts at rendering/measurement start and restore task-local state."""
    fonts = config.resolve_fonts()
    token = _current.set(config)
    try:
        with font_context(fonts):
            yield
    finally:
        _current.reset(token)
