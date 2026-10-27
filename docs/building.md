# Build and maintain the documentation

## First local build

From the repository root, using the project's pyenv-selected Python 3.12+:

```sh
uv sync --group docs
uv run --group docs sphinx-build -W --keep-going -b html docs docs/_build/html
```

Open `docs/_build/html/index.html` in your browser. There is no web service or
account to configure. The output is a static site; this setup does not publish it.
`-W` makes warnings fail the build, and `--keep-going` reports all warnings.

The build runs all tutorial examples before reading pages, so a fresh checkout
does not need generated images in Git. It requires a discoverable sans-serif
font, XeLaTeX, dvisvgm, and the TeX packages used by the examples (standalone,
amsmath, TikZ, and their dependencies). Missing tools or failed examples stop
the build rather than silently leaving stale or missing pictures.

To regenerate just the examples:

```sh
uv run python -m examples.tutorial.render_all
```

## What to edit

- Tutorial prose: `docs/tutorial/en/` and corresponding `docs/tutorial/zh/`.
- Drawing code: `examples/tutorial/`, mirrored under `examples/output/tutorial/`.
- API descriptions: Google-style docstrings beside the implementation in `src/pdl/`.
- API organization: curated pages in `docs/api/`, using Sphinx autodoc.
- Site configuration: `docs/conf.py`.

MyST parses Markdown. Its `literalinclude` directive inserts actual example
source, selecting only the drawing region between `tutorial-start` and
`tutorial-end` markers. The first chapter intentionally includes file-saving
code; later chapters omit it. Edit the example instead of copying another
version of its code into a page. Plain Markdown viewers do not expand these
Sphinx directives; use the built site for code-and-picture reading.

Autodoc imports the library and extracts signatures/docstrings. Napoleon reads
Google-style Args, Returns, and Raises sections. Keep type annotations in
signatures, and explain units, position meanings, mutation, capture, and errors
in prose. The central API reference uses English docstrings for both tutorials;
it is not a separately translated Chinese API manual.

## Review a change

Build with warnings treated as errors. Read both language pages and inspect the
actual example images, especially before/after comparisons and guide marks.
The site does not use screenshot baselines or guarantee identical rendering
between SVG and TikZ. Do not commit `_build` or `examples/output`.

中文：先运行上面的两条构建命令，再用浏览器打开生成的 index.html。
构建会自动生成全部教程图片，需要可用字体及 XeLaTeX/dvisvgm 等外部工具。
正文代码直接从示例中截取，不要在文档里维护第二份代码。
API reference 来自英文 docstring，中英文教程链接到同一份接口说明。

Tool documentation: [Sphinx autodoc](https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html),
[Napoleon](https://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html),
[MyST Parser](https://myst-parser.readthedocs.io/en/latest/).
