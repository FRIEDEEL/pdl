# 1.3 描边与填充

圆的定义决定边界在哪里，`Style` 决定怎样把它画出来。
这一章保持圆的位置和半径不变，每次只改一点外观。

## 给轮廓换个颜色

```{literalinclude} ../../../../examples/tutorial/basics/stroke.py
:language: python
:start-at: from pdl import
:end-before: output =
```

![stroke](../../../../examples/output/tutorial/basics/stroke.svg)

[完整源文件](../../../../examples/tutorial/basics/stroke.py)

`stroke` 是轮廓的颜色，也就是描边颜色。
`line_width=0.5` 把描边宽度设为 0.5 mm，不会改变圆的半径。
描边沿着边界两侧展开。默认线宽是 1 mm，因此这里的轮廓比上一章更细。

`Color(red, green, blue)` 的三个数分别表示红、绿、蓝，每个数都在 0 到 1 之间。
例如 `Color(1, 0, 0)` 是红色，`Color(0, 0, 0)` 是黑色，
`Color(1, 1, 1)` 是白色。例子中蓝色分量比另外两个分量大。

## 再给内部填色

保留蓝色描边，在圆里面填上浅蓝色：

```{literalinclude} ../../../../examples/tutorial/basics/fill.py
:language: python
:start-at: from pdl import
:end-before: output =
```

![fill](../../../../examples/output/tutorial/basics/fill.svg)

[完整源文件](../../../../examples/tutorial/basics/fill.py)

这里仅增加了 `light_blue` 颜色，并在样式中加入 `fill=light_blue`。
`stroke` 和 `fill` 分别控制轮廓和内部，可以独立设置。

## 去掉轮廓

如果只想要一个实心圆，把 `stroke` 设为 `None`：

```{literalinclude} ../../../../examples/tutorial/basics/fill_only.py
:language: python
:start-at: from pdl import
:end-before: output =
```

![fill only](../../../../examples/output/tutorial/basics/fill_only.svg)

[完整源文件](../../../../examples/tutorial/basics/fill_only.py)

`None` 表示不画描边。它与白色描边不同，白色描边仍然会覆盖下面的内容。
同样，`fill=None` 表示不填内部，而不是用白色填充。
默认就是 `fill=None`，所以本章第一个例子不必专门写它。

## 给三个图形分别设置样式

多边形和矩形也使用相同的样式选项。下面给上一章的三个图形分别设置不同的外观：

```{literalinclude} ../../../../examples/tutorial/basics/colored_shapes.py
:language: python
:start-at: from pdl import
:end-before: output =
```

![colored shapes](../../../../examples/output/tutorial/basics/colored_shapes.svg)

[完整源文件](../../../../examples/tutorial/basics/colored_shapes.py)

三角形只有蓝色描边；矩形填成橙色，保留默认的黑色描边；圆填成绿色，没有描边。
把样式单独起名，可以让图形定义更容易阅读，也方便把同一种样式用在多个物件上。

## 自己改一下

在 `fill.py` 中，把 `line_width=0.5` 改成 `line_width=2`，重新运行。
圆的边界没有移动，但描边会向边界两侧变粗。
然后把 `fill` 改成 `None`，圆就重新变成只有轮廓的样子。

到这里，你已经能放置基本图形，并设置描边和填充。
下一章让两个图形重叠，看看绘制顺序怎样影响遮挡。


---

[本篇目录](index.md)
