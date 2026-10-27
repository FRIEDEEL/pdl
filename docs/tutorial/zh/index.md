# 跟着例子学 pdl

按顺序跟着例子画图。每一步都有小段代码和实际生成的 SVG 图片。
开始时不用了解渲染器，最后几章再解释内部过程。

第一章交代怎样保存文件，后续正文只保留绘图代码，附上完整可运行脚本的链接。
脚本在仓库根目录运行；如果直接复制正文片段，可自行加上 `canvas.save("drawing.svg")`。
构建网站时会自动生成图片。直接用 Markdown 预览时，先运行
`uv run python -m examples.tutorial.render_all`。
完整运行需要 XeLaTeX 和 dvisvgm，请先看第五章的环境说明。

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
19-images
20-gradients
21-project-3d
22-plane-artwork
23-d10
```

[English version](../en/index.md) · [API 接口文档](../../api/index.md)
