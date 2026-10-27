# 13. 从物件到图片

前面我们一直在描述画什么。这一章看看这些描述什么时候变成有确定尺寸的图形，
又怎样变成输出文件中的内容。

## 三个步骤

1. **Author：**创建形状、文字、放置和引用。draw 记录加入画布时的状态，不测量字体。
2. **Resolve：**使用当前画布设置，求出位置、文字尺寸，再应用视口映射。
3. **Export：**输出适配器写成 SVG 或 TikZ；能保留原生物件时优先保留，其他情况按需拆解。

Resolved 并不意味着一切都变成 Path。矩形、圆、测量后的文字和节点仍可以保留身份。
例如 TikZ 可以在平移、旋转下使用原生节点，更一般的仿射变换则可能需要拆解。
不同后端不保证逐像素一致。

## 保留一次确定结果

```{literalinclude} ../../../examples/tutorial/advanced/resolved.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![原标签与后来移动后的标签](../../../examples/output/tutorial/advanced/resolved.svg)

[完整可运行示例](../../../examples/tutorial/advanced/resolved.py)

canvas.resolve(label) 在移动 Entity 前测量原标签。
主画布显示先后记录的两个状态，copy 画布只接收已经固定的原结果：

![固定的原标签](../../../examples/output/tutorial/advanced/resolved-copy.svg)

快照固定了位置和文字度量，但原生文字输出仍可能需要字体或 TeX 资源。
它不是位图，也不是自带字体的独立文件。
把它放进另一块画布时，目标画布的映射仍会作用于这些确定的几何。

普通渲染每次重新求值。引用捕获的是作者描述，resolved 结果则连本次度量也固定下来。
因此改字体可能影响普通引用，但不会重新测量已确定快照的文字尺寸。

## 选择输出

`canvas.render("svg")` 返回 XML 字符串，`canvas.render("tikz")` 返回 TeX 源码；
后者可以用 standalone=False 请求可嵌入的 TikZ picture。
save 写出源码，并可进一步编译 TikZ PDF。
文件名后缀不会替你选择后端，保存时应让后缀和 backend 参数一致。

## 自己试试

在第二次 draw 前把标签移得更远。复制出的快照仍停在原位置。
求值依赖不会自动绘制被引用的物件，也不会重排遮挡顺序。

接口说明：{py:meth}`pdl.Canvas.resolve`、{py:class}`pdl.ResolvedGraphic`、
{py:meth}`pdl.Canvas.render`。另见 [TikZ 输出说明](../../tikz-output_zh.md)。

---

[上一章：画布适配](12-viewports.md) · [下一章：TeX 渲染](14-tex-rendering.md)
