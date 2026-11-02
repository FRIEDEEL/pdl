"""Enforce package ownership, import direction, and the single Author model."""

import ast
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parents[2]
SOURCE = ROOT / "src/pdl"


def imports(file: Path) -> list[str]:
    result: list[str] = []
    for node in ast.walk(ast.parse(file.read_text())):
        if isinstance(node, ast.ImportFrom) and node.module is not None:
            result.append(node.module)
        elif isinstance(node, ast.Import):
            result.extend(alias.name for alias in node.names)
    return result


def test_domain_and_adapter_import_directions() -> None:
    for file in SOURCE.rglob("*.py"):
        path = file.relative_to(SOURCE).as_posix()
        for module in imports(file):
            assert not module.startswith(("pdl_old", "pdl.foundation", "pdl.author.placement")), (
                path,
                module,
            )
            if path.startswith("author/util/"):
                assert not module.startswith("pdl."), (path, module)
            if path.startswith("author/"):
                assert not module.startswith(("pdl.canvas", "pdl.backends", "pdl.extensions")), (
                    path,
                    module,
                )
            if path.startswith("author/style/"):
                assert not module.startswith(
                    ("pdl.author.entity", "pdl.author.geometry", "pdl.author.transform")
                ), (path, module)
            if path.startswith("author/geometry/"):
                assert not module.startswith("pdl.author.entity"), (path, module)
                if module.startswith("pdl.author.style"):
                    assert module in (
                        "pdl.author.style.font",
                        "pdl.author.style.font_policy",
                        "pdl.author.style.typography",
                    ), (path, module)
            if path.startswith("backends/") and module.startswith("pdl.canvas"):
                assert module == "pdl.canvas.records", (path, module)
            if path.startswith("extensions/"):
                assert not module.startswith(("pdl.canvas", "pdl.backends")), (path, module)


def test_source_dependencies_are_not_hidden_in_function_imports() -> None:
    for file in SOURCE.rglob("*.py"):
        for node in ast.walk(ast.parse(file.read_text())):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                assert not any(
                    isinstance(child, (ast.Import, ast.ImportFrom)) for child in ast.walk(node)
                ), file


def test_importing_the_core_does_not_load_optional_extensions() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "import sys; import pdl.author; from pdl import Circle, Canvas; "
            "assert not any(k.startswith('pdl.extensions') for k in sys.modules); "
            "assert not any(k.startswith('pdl_old') for k in sys.modules)",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr


def test_captured_extensions_are_ordinary_entity_groups() -> None:
    from pdl import Canvas, Entity, Group, Node, Scene3D, Text, regular_polyhedron
    from pdl.author.entity.capture import Composite, walk
    from pdl.author.geometry.protocols import PathSource

    canvas = Canvas(60, 40)
    canvas.add(Group(Scene3D((regular_polyhedron("cube"),)).project(), Node(Text("Label"))))
    for leaf in walk(canvas.drawings):
        assert isinstance(leaf, Entity)
        assert not isinstance(leaf, Composite)
        assert isinstance(leaf.geometry, PathSource)
        assert not hasattr(leaf, "transform")
