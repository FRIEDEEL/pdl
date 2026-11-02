# SVG, TikZ, and PDF output

Adapters encode captured Entity geometry and Style. Python determines diagram
shapes, ports, and numerical placement. TikZ text nodes typeset at determined
baselines; they do not perform diagram layout or return anchor positions.

canvas.render() returns SVG, and render("tikz") returns a standalone LaTeX
document. standalone=False returns an embeddable fragment; use latex_preamble()
for its packages/macros. Explicitly select backend="tikz" when saving; a filename
suffix does not select an adapter.

tikz_mode="tex" saves final source, auto compiles when an engine is available,
and pdf requires compilation. Measuring a TeX Entity can still invoke
XeLaTeX/dvisvgm during submission even for source-only output. XeLaTeX is the
default final compiler; native fonts need fontspec. Geometry-only documents may
use another suitable LaTeX engine. Failures preserve source and report logs;
auxiliary files use a temporary directory unless requested otherwise.

SVG embeds image bytes. Saved TikZ copies content-addressed assets beside the
source; move that asset directory with the document. Gradients remain vector
fills. Text retains native form under orientation-preserving similarities; TeX
retains source under translation/rotation. TeX scaling and other text deformation
lower measured outlines. Rich/colored TeX SVG may remain embedded, while
unsupported path conversion fails, including when viewport fitting scales it.

Native font environments and shaping can produce different SVG/LaTeX pixels.
Geometry and placement follow captured measurement policy; exact raster equality
and readable generated-code structure are not promised.

[Tutorial](tutorial/en/06-output/index.md) · [中文说明](tikz-output_zh.md)
