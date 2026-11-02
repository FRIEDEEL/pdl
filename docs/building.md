# Build the documentation and examples

Select Python 3.12+ with pyenv, then use uv for the project environment. From the
repository root, run `uv sync --group docs`. Runtime dependencies remain fontTools
and uharfbuzz; docs use Sphinx, MyST, Napoleon, and Furo.

SVG text needs a usable system font or explicit Font file. TeX examples and
measurement need XeLaTeX and dvisvgm, with TikZ, standalone, amsmath, amssymb,
fontspec, and example font resources. Native text in SVG references installed
font families. examples/_shared/config.py selects the example fonts explicitly.

```sh
uv run python -m examples.tutorial.render_all
uv run python -m examples.tools.render_all --tikz-mode pdf
uv run --group docs sphinx-build -W --keep-going -b html docs docs/_build/html
```

The Sphinx build runs the tutorial and linked case-study generators before
reading source includes/images. Open docs/_build/html/index.html. English lessons
live in tutorial/en, corresponding Chinese lessons in tutorial/zh, and the shared
API uses English source docstrings. Update runnable sources and regenerate their
actual outputs when editing a lesson. Keep comparison references in transformed
illustrations. Generated outputs and build artifacts remain outside Git.

```sh
uv run ruff check .
uv run ruff format --check .
uv run pyright
uv run pytest
uv build
```

The active implementation is src/pdl and its tests mirror modules under tests.
Archived src/pdl_old/tests_old are review references and are excluded from checks
and distributions. Reader examples are included in strict type checking. External
integration tests report skips when required tools/fonts are unavailable; report
those limitations rather than claiming an unexecuted rendering check passed.
