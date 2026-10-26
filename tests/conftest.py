"""Explicit test fonts from the test environment; no library font fallback."""

import os
import shutil
import subprocess
from pathlib import Path

import pytest

from pdl.text import Font


@pytest.fixture
def font() -> Font:
    configured = os.environ.get("PDL_TEST_FONT")
    candidates = [configured] if configured else []
    kpsewhich = shutil.which("kpsewhich")
    if kpsewhich:
        result = subprocess.run(
            [kpsewhich, "texgyreheros-regular.otf"], capture_output=True, text=True, check=False
        )
        candidates.append(result.stdout.strip())
    candidates += [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
    ]
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            return Font(candidate)
    pytest.skip("Set PDL_TEST_FONT to a static Latin TTF/OTF font.")
