# 跟着例子学 pdl

从一个写着“Hello world”的方框开始，再画几个图形，给它们描边、填色。
每一步都有完整的 Python 脚本和对应的 SVG 图片，不要求你先了解 pdl 的内部渲染过程。

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

正文代码块是所链接示例文件的完整副本。后续修改教程时，需要让代码块和示例源码保持一致。

[English version](../en/index.md)
