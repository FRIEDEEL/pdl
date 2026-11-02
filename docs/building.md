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
uv run --group docs python docs/build.py
```

The build runs the tutorial and linked case-study generators once, then builds
independent English and Chinese sites with Sphinx warnings treated as errors.
Open `docs/_build/html/index.html` to choose a language, or go directly to
`docs/_build/html/en/index.html` or `docs/_build/html/zh/index_zh.html`.
Each site has its own navigation, interface language, and search index. Every
translated page links to its exact counterpart. The API reference is generated
only in the English site; the Chinese site provides clearly labeled links to it.

English lessons live in tutorial/en, corresponding Chinese lessons in tutorial/zh.
Top-level Chinese pages use the `_zh.md` suffix, including the Chinese homepage
`index_zh.md`. Corresponding filenames determine the language-switch links.
Examples and generated images are shared by both builds. Update runnable sources and regenerate their
actual outputs when editing a lesson. Keep comparison references in transformed
illustrations. Generated outputs and build artifacts remain outside Git.

To build one language directly, set `PDL_DOCS_LANGUAGE` to `en` or `zh` and keep
the output directories separate:

```sh
PDL_DOCS_LANGUAGE=en uv run --group docs sphinx-build -W --keep-going -b html docs docs/_build/html/en
PDL_DOCS_LANGUAGE=zh uv run --group docs sphinx-build -W --keep-going -b html docs docs/_build/html/zh
```

These direct commands each regenerate examples. `docs/build.py` generates them
in the English build and explicitly reuses them for the subsequent Chinese build.

## Maintain the API reference

Mirror `src/pdl/` under `docs/api/`: each package's `__init__.py` corresponds
to `index.md`, and each other Python module corresponds to a Markdown page with
the same relative path and stem. Add its page and parent toctree entry when adding
a module. Keep package re-export tables linked to the defining module; document
each class or function in full only at its definition. Autodoc reads signatures
and docstrings from the active source tree, including backend and utility modules.
Internal modules remain labeled as implementation details.

When moving a module, update reference links in both language guides and the
Chinese API entry page. The generated API content remains English-only.

```sh
uv run ruff check .
uv run ruff format --check .
uv run pyright
uv run pytest
uv build
```

The active implementation is src/pdl and its tests mirror modules under tests.
The previous implementation and tests are available in Git history rather than
the working tree. Reader examples are included in strict type checking. External
integration tests report skips when required tools/fonts are unavailable; report
those limitations rather than claiming an unexecuted rendering check passed.
