# Learn to draw with pdl

Follow the chapters in order. Each step has a small example and its actual SVG
output. Begin with no knowledge of the renderer; the last chapters explain
what happens behind the scenes.

The first chapter explains saving files. Later code blocks show only drawing
code; each links to a complete runnable script. Run those scripts from the
repository root, or append `canvas.save("drawing.svg")` to a snippet yourself.
The site build generates all images automatically. For Markdown previews,
run `uv run python -m examples.tutorial.render_all` first. TeX examples need
XeLaTeX and dvisvgm; see chapter 5 before running the full set.

```{toctree}
:maxdepth: 1

01-hello-world
02-shapes
03-stroke-and-fill
04-drawing-order
05-text-and-tex
06-transforms
07-coordinate-systems
08-anchors
09-groups
10-paths
11-geometry-queries
12-viewports
13-rendering
14-tex-rendering
15-fill-rules
16-editable-groups
17-gathers
18-layers
groups-layers-gathers
19-images
20-gradients
21-project-3d
22-plane-artwork
23-d10
24-perspective
25-depth-order
```

[中文版](../zh/index.md) · [API reference](../../api/index.md)
