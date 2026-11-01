"""Renderer-level font discovery and document configuration."""

from __future__ import annotations

import os
import shutil
import subprocess
from collections.abc import Generator
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from pdl.foundation.typography.shaping import Font, font_context
from pdl.foundation.typography.tex import TeXConfig


@dataclass(frozen=True)
class RendererConfig:
    """Default font candidates and a shared LaTeX environment.

    Args:
        fonts: Ordered Font objects or strings. Strings can be existing paths,
            TeX-discoverable filenames, or installed fontconfig family names.
            An empty tuple requests a system sans-serif font when text needs one.
        tex: Shared TeXConfig, or ``None`` for the standard default environment.

    An explicit Text.font overrides these defaults. SVG native text references
    installed font families rather than embedding files; viewing requires suitable
    fonts. Native SVG and LaTeX metrics may differ slightly.
    """

    fonts: tuple[Font | str, ...] = ()
    tex: TeXConfig | None = None

    def resolve_fonts(self) -> tuple[Font, ...]:
        if not self.fonts:
            return default_fonts()
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


@lru_cache(maxsize=1)
def default_fonts() -> tuple[Font, ...]:
    """Find a usable default without making font discovery a geometry dependency."""
    try:
        return (resolve_font("sans-serif"),)
    except FileNotFoundError:
        pass
    candidates = (
        Path("/System/Library/Fonts/Helvetica.ttc"),
        Path("/System/Library/Fonts/Supplemental/Arial.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
        Path("/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf"),
        Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts" / "arial.ttf",
    )
    for candidate in candidates:
        if candidate.is_file():
            return (Font(candidate),)
    try:
        return (resolve_font("texgyreheros-regular.otf"),)
    except FileNotFoundError as error:
        raise FileNotFoundError(
            "No default font found; set RendererConfig(fonts=(...)) to an installed font."
        ) from error


_current: ContextVar[RendererConfig] = ContextVar("pdl_renderer", default=RendererConfig())


def current_renderer() -> RendererConfig:
    return _current.get()


@contextmanager
def rendering(config: RendererConfig) -> Generator[None, None, None]:
    """Resolve fonts at rendering/measurement start and restore task-local state."""
    # Explicit choices are checked at the boundary. The automatic default is
    # lazy so geometry-only drawings and explicitly fonted text work without
    # system font discovery tools.
    fonts = config.resolve_fonts() if config.fonts else default_fonts
    token = _current.set(config)
    try:
        with font_context(fonts):
            yield
    finally:
        _current.reset(token)


# Measurement and rendering share exactly the same resource policy.
measurement = rendering
