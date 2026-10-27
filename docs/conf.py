"""Build the bilingual pdl manual and public Python API reference."""

import subprocess
import sys
from pathlib import Path

from sphinx.application import Sphinx

ROOT = Path(__file__).resolve().parents[1]
project = "pdl"
author = "LiGuang"
release = "0.1.0"
extensions = ["myst_parser", "sphinx.ext.autodoc", "sphinx.ext.napoleon"]
source_suffix = {".md": "markdown", ".rst": "restructuredtext"}
root_doc = "index"
exclude_patterns = ["_build", "README.md"]
html_theme = "furo"
html_static_path = ["_static"]
html_css_files = ["tutorial.css"]
html_title = "pdl — Python Drawing Library"
language = "en"
myst_heading_anchors = 3
myst_enable_extensions = ["colon_fence"]
autodoc_member_order = "bysource"
autodoc_typehints = "signature"
autodoc_typehints_format = "short"
autodoc_preserve_defaults = True
napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_use_param = True
napoleon_use_rtype = False


def generate_examples(app: Sphinx) -> None:
    """Create tutorial images before Sphinx reads image and include directives."""
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

    for module in ("examples.spatial.platonic_solids", "examples.spatial.planes"):
        subprocess.run([sys.executable, "-m", module], cwd=ROOT, check=True)


def setup(app: Sphinx) -> None:
    """Register deterministic, local example generation for every build."""
    app.connect("builder-inited", generate_examples)
