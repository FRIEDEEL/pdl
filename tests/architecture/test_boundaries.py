"""Keep the architectural dependency direction executable and reviewable."""

import ast
import subprocess
import sys
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[2] / "src" / "pdl"


def test_module_dependency_boundaries() -> None:
    violations: list[str] = []
    for file in SOURCE.rglob("*.py"):
        relative = file.relative_to(SOURCE)
        owner = relative.parts[0]
        for node in ast.walk(ast.parse(file.read_text())):
            if not isinstance(node, (ast.ImportFrom, ast.Import)):
                continue
            modules = (
                [node.module or ""]
                if isinstance(node, ast.ImportFrom)
                else [alias.name for alias in node.names]
            )
            for module in modules:
                if not module.startswith("pdl."):
                    continue
                target = module.split(".")[1]
                allowed = {
                    "foundation": {"foundation"},
                    "author": {"foundation", "author"},
                    "extensions": {"foundation", "author", "extensions"},
                    "canvas": {"foundation", "author", "canvas", "backends"},
                    "backends": {"foundation", "author", "backends", "canvas"},
                }.get(owner)
                if allowed is not None and target not in allowed:
                    violations.append(f"{relative}:{node.lineno} imports {module}")
                if owner == "backends" and target == "canvas" and module != "pdl.canvas.records":
                    violations.append(f"{relative}:{node.lineno} depends on Canvas implementation")
    assert not violations, "\n".join(violations)


def test_foundation_and_core_import_without_extensions_or_backends() -> None:
    checks = [
        (
            "import pdl.foundation.typography.tex",
            ("pdl.author", "pdl.canvas", "pdl.backends", "pdl.extensions"),
        ),
        ("from pdl import Circle, Text, Style", ("pdl.canvas", "pdl.backends", "pdl.extensions")),
        ("from pdl import Canvas, Circle", ("pdl.extensions",)),
    ]
    for statement, forbidden in checks:
        script = (
            "import sys\n"
            + statement
            + "\n"
            + f"forbidden = {forbidden!r}\n"
            + "assert not any(n == p or n.startswith(p + '.') "
            + "for n in sys.modules for p in forbidden)"
        )
        subprocess.run([sys.executable, "-c", script], check=True, capture_output=True, text=True)
