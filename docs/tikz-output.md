# TikZ source and PDF output

`Canvas.render("tikz")` returns standalone TeX source as a string. Use
`standalone=False` for an embeddable fragment. Rendering itself does not compile
that document to PDF. Measuring `TeX` objects can still require the existing
XeLaTeX/dvisvgm typography pipeline before export.

`Canvas.save("figure.tex", backend="tikz")` writes the source and, by default,
tries XeLaTeX to create `figure.pdf` beside it. The options are:

- `tikz_mode="auto"`: compile if the selected executable exists; otherwise keep
  only the source. This is the default.
- `tikz_mode="tex"`: save source without compiling the output document.
- `tikz_mode="pdf"`: require the compiler; absence raises `FileNotFoundError`.
- `keep_intermediates=False`: compile into a temporary directory and copy only
  the PDF to the destination. Set True to keep `.aux`, `.log`, and other compiler
  artifacts beside the source, including diagnostics when compilation fails.
- `engine="xelatex"`: select the executable. Other engines must support the
  packages and fonts used by your document; no alternative engine is selected
  automatically.

Compilation runs from the source directory so relative TeX inputs resolve there.
Shell escape is disabled and compilation has a 60-second timeout. Compiler
failures raise an error with captured diagnostics; they do not silently downgrade
to source-only output. The source is retained. Existing PDFs and auxiliary files
from previous runs are not removed; a failed/skipped compile does not refresh an
existing PDF. Use a `.tex` filename for TikZ saves.

```python
canvas.save("figure.tex", backend="tikz", tikz_mode="auto")
canvas.save("debug.tex", backend="tikz", tikz_mode="pdf", keep_intermediates=True)
```

Generate all examples with the same compilation helper:

```sh
uv run python -m examples.tools.render_all
uv run python -m examples.tools.render_all --tikz-mode tex
uv run python -m examples.tools.render_all --tikz-mode pdf --keep-intermediates
```

The integration tests also exercise this helper with real LaTeX engines and check
that the default output directory contains only TeX and PDF files.
