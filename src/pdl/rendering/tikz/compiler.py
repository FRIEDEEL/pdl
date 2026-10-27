"""Optional PDF compilation for saved TikZ documents."""

import shutil
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Literal

TikZMode = Literal["auto", "tex", "pdf"]


def compile_pdf(
    source: Path,
    *,
    mode: TikZMode = "auto",
    keep_intermediates: bool = False,
    engine: str = "xelatex",
) -> Path | None:
    """Compile a saved document, optionally keeping compiler artifacts.

    Args:
        source: Existing standalone TeX document.
        mode: Source only, optional compilation, or required compilation.
        keep_intermediates: Keep compiler artifacts beside the source.
        engine: LaTeX executable; XeLaTeX supports native pdl fonts.

    Returns:
        The PDF path, or None when compilation is disabled or unavailable.
    """
    if mode not in ("auto", "tex", "pdf"):
        raise ValueError(f"Unknown TikZ output mode: {mode}")
    if mode == "tex":
        return None
    executable = shutil.which(engine)
    if executable is None:
        if mode == "pdf":
            raise FileNotFoundError(f"Required LaTeX engine {engine!r} is unavailable.")
        return None
    source = source.resolve()
    with TemporaryDirectory(prefix="pdl-tikz-") as temporary:
        output = source.parent if keep_intermediates else Path(temporary)
        result = subprocess.run(
            [
                executable,
                "-no-shell-escape",
                "-interaction=nonstopmode",
                "-halt-on-error",
                f"-output-directory={output}",
                source.name,
            ],
            cwd=source.parent,
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
        if result.returncode:
            raise RuntimeError(
                f"TikZ compilation failed for {source}:\n" + (result.stdout + result.stderr)[-8000:]
            )
        generated = output / source.with_suffix(".pdf").name
        destination = source.with_suffix(".pdf")
        if generated != destination:
            shutil.copyfile(generated, destination)
        return destination
