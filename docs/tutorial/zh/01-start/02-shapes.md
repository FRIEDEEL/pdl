# 1.2 画几个基本图形

上一章的 `Node` 帮我们在文字外面画好了方框。
这一章先不放文字，直接画图形。

## 三角形、矩形和圆

```{literalinclude} ../../../../examples/tutorial/basics/shapes.py
:language: python
:start-at: from pdl import
:end-before: output =
```

![shapes](../../../../examples/output/tutorial/basics/shapes.svg)

[完整源文件](../../../../examples/tutorial/basics/shapes.py)

你会看到三个只有黑色轮廓、没有填充的图形。这是没有另外指定样式时的默认效果。

`Polygon` 按顺序连接给出的顶点，最后自动连回第一个顶点。
这里三角形的底边从 `(10, 10)` 到 `(30, 10)`，顶点是 `(20, 30)`。
多给几个顶点，就能画出其他多边形。

`Rectangle((40, 10), width=25, height=20)` 的第一个坐标是**左下角**，
从那里向右延伸 25 mm，向上延伸 20 mm。因此右上角是 `(65, 30)`。

`Circle((85, 20), radius=10)` 指定的是**圆心和半径**。
这个圆的左右边缘分别在 x = 75 和 x = 95，上下边缘分别在 y = 30 和 y = 10。

这里要留意：不同物件的定位方式不完全一样。Node 用中心定位，Rectangle 用左下角，
Circle 用圆心，而 Polygon 直接使用你给出的各个顶点。

## 把坐标画出来看看

我们换一块小画布，只放一个圆。下面的浅灰线把圆心连到 x、y 轴上。
`(20, 15)` 表示从原点向右 20 mm、向上 15 mm，起点不是圆的边缘。

```{literalinclude} ../../../../examples/tutorial/basics/coordinates.py
:language: python
:start-at: from pdl import
:end-before: output =
```

![coordinates](../../../../examples/output/tutorial/basics/coordinates.svg)

[完整源文件](../../../../examples/tutorial/basics/coordinates.py)

`# Optional guides` 之后的代码只负责画坐标轴、辅助线和标签。
这些标记也是普通的绘图物件，不是自动显示的坐标背景。
删掉这一整段，圆的位置也不会改变。坐标轴恰好位于画布边缘，因此轴线的一半线宽会被裁掉。

`Line` 连接两个点，`Text` 用来标注文字。后面会进一步讲解文字和样式；
你不需要在每张图里都写上这些辅助标记。

## 自己改一下

在第一个脚本里，把矩形的宽度从 `25` 改成 `15`。
左边缘仍然在 x = 40，只有右边缘向左移动。
再把圆的半径从 `10` 改成 `6`，圆会缩小，但圆心仍在 `(85, 20)`。

在坐标示例里，把圆心改成 `(20, 22)`，圆会向上移动。
辅助线是另外画的，所以它们仍然指向原来的圆心；要一起移动，需要同时修改它们的坐标。


---

[本篇目录](index.md)
