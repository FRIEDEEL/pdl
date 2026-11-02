"""Build the bilingual pdl manual and public Python API reference."""

import os
import posixpath
import subprocess
import sys
import tomllib
from pathlib import Path

from docutils import nodes
from sphinx.application import Sphinx

ROOT = Path(__file__).resolve().parents[1]
project = "pdl"
author = "LiGuang"
with (ROOT / "pyproject.toml").open("rb") as project_file:
    release = tomllib.load(project_file)["project"]["version"]
extensions = ["myst_parser", "sphinx.ext.autodoc", "sphinx.ext.napoleon"]
source_suffix = {".md": "markdown", ".rst": "restructuredtext"}
DOCS_LANGUAGE = os.environ.get("PDL_DOCS_LANGUAGE", "en")
if DOCS_LANGUAGE not in {"en", "zh"}:
    raise ValueError("PDL_DOCS_LANGUAGE must be 'en' or 'zh'.")
root_doc = "index" if DOCS_LANGUAGE == "en" else "index_zh"
exclude_patterns = ["_build", "README.md"]
if DOCS_LANGUAGE == "en":
    exclude_patterns += ["tutorial/zh", "*_zh.md"]
else:
    exclude_patterns += ["tutorial/en", "api"]
    exclude_patterns += [
        path.name for path in (ROOT / "docs").glob("*.md") if not path.stem.endswith("_zh")
    ]
templates_path = ["_templates"]
html_theme = "furo"
html_static_path = ["_static"]
html_css_files = ["tutorial.css"]
html_title = "pdl — Python Drawing Library" if DOCS_LANGUAGE == "en" else "pdl — Python 绘图库"
language = "en" if DOCS_LANGUAGE == "en" else "zh_CN"
myst_heading_anchors = 3
myst_enable_extensions = ["colon_fence", "substitution"]
autodoc_member_order = "bysource"
autodoc_typehints = "signature"
autodoc_typehints_format = "short"
autodoc_preserve_defaults = True
napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_use_param = True
napoleon_use_rtype = False


def git_value(*args: str) -> str:
    """Read build metadata, including when Git metadata is unavailable."""
    try:
        return subprocess.check_output(
            ["git", *args], cwd=ROOT, text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unavailable"


commit = git_value("rev-parse", "--short", "HEAD")
if git_value("status", "--porcelain", "--untracked-files=no") not in ("", "unavailable"):
    commit += " (working tree modified)"
myst_substitutions = {
    "build_version": release,
    "build_commit": commit,
    "build_branch": git_value("branch", "--show-current") or "detached HEAD",
}


def generate_examples(app: Sphinx) -> None:
    """Create tutorial images before Sphinx reads image and include directives."""
    if os.environ.get("PDL_DOCS_SKIP_EXAMPLES") == "1":
        return
    subprocess.run(
        [sys.executable, "-m", "examples.tutorial.render_all"],
        cwd=ROOT,
        check=True,
    )

    subprocess.run(
        [sys.executable, "-m", "examples.composition.sandwich"],
        cwd=ROOT,
        check=True,
    )
    subprocess.run(
        [sys.executable, "-m", "examples.flowcharts.growing"],
        cwd=ROOT,
        check=True,
    )

    for module in (
        "examples.spatial.platonic_solids",
        "examples.spatial.planes",
        "examples.spatial.curved_solids",
        "examples.spatial.d10",
        "examples.spatial.visibility",
        "examples.spatial.material_probe",
    ):
        subprocess.run([sys.executable, "-m", module], cwd=ROOT, check=True)


def language_link(
    app: Sphinx,
    pagename: str,
    templatename: str,
    context: dict[str, object],
    doctree: nodes.document | None,
) -> None:
    """Link to the matching page in the independently built language site."""
    other = "zh" if DOCS_LANGUAGE == "en" else "en"
    if pagename.startswith("tutorial/"):
        counterpart = pagename.replace(f"tutorial/{DOCS_LANGUAGE}/", f"tutorial/{other}/", 1)
    elif pagename.startswith("api/") or pagename == "py-modindex":
        counterpart = "api_zh"
    elif pagename == "api_zh":
        counterpart = "api/index"
    elif pagename in {"search", "genindex"}:
        counterpart = pagename
    elif DOCS_LANGUAGE == "en":
        counterpart = f"{pagename}_zh"
    else:
        counterpart = pagename.removesuffix("_zh")
    current_directory = posixpath.dirname(f"{DOCS_LANGUAGE}/{pagename}.html")
    context["language_url"] = posixpath.relpath(
        f"{other}/{counterpart}.html", start=current_directory
    )
    context["docs_language"] = DOCS_LANGUAGE
    context["api_english_only"] = pagename.startswith("api/") or pagename == "py-modindex"


def setup(app: Sphinx) -> None:
    """Register deterministic, local example generation for every build."""
    app.connect("builder-inited", generate_examples)
    app.connect("html-page-context", language_link)
