# 6.2 TeX 怎样变成图中的内容

公式必须先排版，pdl 才能知道它的宽、高和基线。
即使最终输出是 SVG，也需要先完成这一步。

## 使用共同的 TeX 环境

```{literalinclude} ../../../../examples/tutorial/advanced/tex_pipeline.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![公式和按文字尺寸撑开的节点](../../../../examples/output/tutorial/advanced/tex_pipeline.svg)

[完整可运行示例](../../../../examples/tutorial/advanced/tex_pipeline.py)

TeXConfig 指定包和导言区命令。公式使用这里定义的 energy 命令，
Node 再根据测量出的公式排版框确定外形尺寸。
同一份配置用于测量和原生输出。

## 测量与 SVG 输出

pdl 调用 XeLaTeX 排版片段并报告盒子尺寸，再用 dvisvgm 转换成带基线信息的 SVG 轮廓。
SVG 后端把片段放到图中。它与普通 SVG Text 不同，公式不依赖浏览器重新找到原字体。

测量结果会缓存，依据包括源码、工具版本、配置及显式依赖文件的内容。
可能变化的外部文件应列入 TeXConfig.dependencies。
如果外部 TeX 包发生变化，可在需要时修改 cache_salt 使旧缓存失效。
缓存不会自动发现所有外部 TeX 依赖。

## 原生 TikZ 输出

TikZ 后端保留 LaTeX 源码，把共同导言区加入文档。
编译最终文档时会再次排版，因此片段测量与最终文字之间仍可能有细微差别。
同一份原生 TikZ 文档需要使用兼容的共同 TeXConfig。

完整示例生成 SVG、tex 源码和 PDF。
需要安装 XeLaTeX、dvisvgm、standalone 及配置使用的包。
导入 pdl 或构造 TeX 时不运行这些工具，测量或渲染时才运行。
用 tikz_mode="tex" 只保存源码，可以跳过最终 PDF 编译，
但不能省略公式片段测量所需的工具。

## 自己试试

修改导言区命令，让它定义另一个符号，再运行。公式和外面的节点都会更新。
编译模式、中间文件和嵌入方式见 [TikZ 输出说明](../../../tikz-output_zh.md)。

接口说明：{py:class}`pdl.TeXConfig`、{py:class}`pdl.TeX`、{py:meth}`pdl.Canvas.save`。


---

[本篇目录](index.md)
