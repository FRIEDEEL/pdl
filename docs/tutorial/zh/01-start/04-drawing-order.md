# 1.4 谁挡住谁？

两个物件可以占据画布上的同一块地方。让橙色矩形和蓝色圆重叠，看看谁会挡住谁。

## 先画圆

```{literalinclude} ../../../../examples/tutorial/layout/circle_first.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![矩形后画，遮住圆的一部分](../../../../examples/output/tutorial/layout/circle_first.svg)

[完整可运行示例](../../../../examples/tutorial/layout/circle_first.py)

矩形遮住了圆的右半部分。圆本身仍然是完整的，只是矩形的填充覆盖了它。

## 交换两次 draw 的顺序

图形、坐标、样式都不变，只交换最后两行：

```{literalinclude} ../../../../examples/tutorial/layout/rectangle_first.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![圆后画，遮住矩形的一部分](../../../../examples/output/tutorial/layout/rectangle_first.svg)

[完整可运行示例](../../../../examples/tutorial/layout/rectangle_first.py)

现在圆在前面。**后调用的 draw 画在先调用的上面。**
创建 Python 变量的先后顺序不决定遮挡关系。

这也解释了 `fill=None` 和白色填充的区别：不填充时，内部什么都不画，
下面的物件可以透出来；白色填充则会用白色覆盖下面的物件。

## 自己试试

在第一个例子中，把矩形样式的 `fill` 改成 `None`。
矩形轮廓仍画在前面，但内部会露出蓝色圆。这里用的是已有的绘制顺序，尚未引入 Layer 接口。

接口说明：{py:meth}`pdl.Canvas.draw`、{py:class}`pdl.Style`。


---

[本篇目录](index.md)
