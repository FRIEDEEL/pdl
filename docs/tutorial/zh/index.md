# 跟着例子学 pdl

从一个写着“Hello world”的方框开始，再画几个图形，给它们描边、填色。
每一步都有绘图代码、对应的 SVG 图片和完整可运行示例的链接，不要求你先了解 pdl 的内部渲染过程。

1. [第一张图](01-hello-world.md)
2. [基本图形](02-shapes.md)
3. [描边与填充](03-stroke-and-fill.md)

第一次使用请从第一章的环境准备开始。所有命令都在仓库根目录运行。
每个脚本可以独立运行，图片保存到 `examples/output/tutorial/basics/`。
本地 Markdown 预览里的图片需要先运行对应脚本生成；生成的图片不提交到 Git。

也可以一次生成全部七张图片：

```sh
uv run python -m examples.tutorial.render_all
```

第一章之后，正文代码块只展示绘图部分，省略保存文件和选择输出路径的代码；
链接中的完整示例仍包含这些步骤。如果要自行保存图片，像第一章一样在末尾加上
`canvas.save("drawing.svg")` 即可。后续修改教程时，需要让正文绘图代码与示例源码保持一致。

[English version](../en/index.md)
