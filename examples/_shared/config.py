"""Shared example configuration, explicit fonts and reusable symbols."""

import shutil
import subprocess
from pathlib import Path

from pdl import Color, Font, Style
from pdl.foundation.typography.config import resolve_font

EXAMPLES = Path(__file__).resolve().parents[1]
OUTPUT = EXAMPLES / "output"
BLUE = Color(0.12, 0.33, 0.58)
PALE = Color(0.89, 0.94, 0.98)
ORANGE = Color(0.9, 0.43, 0.16)
INK = Style(stroke=BLUE, line_width=0.45)
LABEL = Style(stroke=None, fill=BLUE)


def tex_font(filename: str) -> Font:
    """Locate an explicitly named example font from the local TeX installation.

    Edit the example to use Font('/path/to/font.otf') on other installations.
    This convenience belongs to examples, not to pdl's font selection policy.
    """
    executable = shutil.which("kpsewhich")
    if executable is None:
        raise FileNotFoundError("Install TeX Live or configure explicit example font paths.")
    result = subprocess.run([executable, filename], capture_output=True, text=True, check=True)
    return Font(result.stdout.strip())


def latin_font() -> Font:
    return resolve_font("sans-serif")


def chinese_font() -> Font:
    system = Path("/System/Library/Fonts/Hiragino Sans GB.ttc")
    return Font(system) if system.is_file() else tex_font("FandolHei-Regular.otf")


def cjk_font() -> Font:
    candidates = sorted(Path("/System/Library/Fonts").glob("*W3.ttc"))
    return Font(candidates[0]) if candidates else tex_font("HaranoAjiGothic-Regular.otf")
