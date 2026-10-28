# 1.5 文字与公式

Node 包含文字和外框。如果只想放文字，不要方框，就用 {py:class}`pdl.Text`。

## 放置普通文字

```{literalinclude} ../../../../examples/tutorial/text/labels.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![两行不同字号的文字，以及对应基线](../../../../examples/output/tutorial/text/labels.svg)

[完整可运行示例](../../../../examples/tutorial/text/labels.py)

两条灰线标出文字的**基线**。Text 的位置与 Node 不同，它不是中心。
默认左对齐时，位置指定左侧的基线参照点。字母大部分在基线上方，有些笔画会伸到下方。
不需要辅助线时，删掉代码中对应的可选部分即可。

`size` 的单位是 TeX 点，不是毫米；一点等于 1/72.27 英寸。
这里使用默认系统字体，因此字形和支持的字符取决于已安装字体。
Text 会照原样显示内容，`$x^2$` 不会自动变成公式。
换行符可以另起一行，但目前不会自动按段落宽度折行。

给文字指定样式时，使用 `Style(stroke=None, fill=...)`。
目前原生文字只支持填充色；不传样式时默认使用黑色。

## 排版一个公式

运行这个例子前，需要安装 XeLaTeX、dvisvgm，以及 LaTeX 的 `standalone` 文档类和
`amsmath` 包。适当配置的 TeX Live 可以提供这些工具。先确认终端能找到：

```sh
xelatex --version
dvisvgm --version
```

```{literalinclude} ../../../../examples/tutorial/text/formula.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![用 LaTeX 排版的公式](../../../../examples/output/tutorial/text/formula.svg)

[完整可运行示例](../../../../examples/tutorial/text/formula.py)

TeX 会解析 LaTeX，美元符号用于进入数学模式。
Python 字符串前的 `r` 可以保留反斜杠，例如 `r"$\frac{a}{b}$"`。
它的位置同样是左侧基线参照点，字号单位同样是 TeX 点。

完整示例会保存 SVG 和原生 TikZ PDF。如果尚未安装这些工具，可以先学习后面不使用
TeX 的章节；普通 Text 的 SVG 输出不需要它们。

## 自己试试

把公式换成 `r"$a^2 + b^2 = c^2$"`，必要时加宽画布。
把普通文字换成 `"First line\nSecond line"`，看看显式换行的效果。
后面的 [TeX 渲染](../06-output/02-tex.md)会进一步解释处理过程。

接口说明：{py:class}`pdl.Text`、{py:class}`pdl.TeX`、{py:class}`pdl.FontStack`。


---

[本篇目录](index.md)
