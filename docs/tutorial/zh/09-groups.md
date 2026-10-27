# 9. 把几个物件组合起来复用

我们用矩形画零件主体，用小圆画连接端口。
现在想放两个这样的零件，并把其中一个旋转，不再分别计算每个部分的位置。

```{literalinclude} ../../../examples/tutorial/layout/groups.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![同一个组件在两个位置重复使用](../../../examples/output/tutorial/layout/groups.svg)

[完整可运行示例](../../../examples/tutorial/layout/groups.py)

Group 收集一组有顺序的 Drawing。每条 Drawing 包含物件，以及可选的样式和放置变换。
组件内部的矩形以 `(0, 0)` 为中心，端口在 `(11, 0)`。

first 和 second 复用同一个组件定义，只是放置方式不同。
第二个实例先旋转局部坐标，再平移到 `(60, 20)`。
主体和端口一起移动，两者之间的相对距离不变，原始组件也不会被修改。

如果想拿到某个实例的具体部分，可以用 `second.child(1)` 访问端口。
它的锚点包含第二个实例累积的变换。
直接取 Group 的锚点，得到的则是整体轴对齐包围盒上的点；连接具体端口时通常不该用它代替。

子物件有显式样式时，使用它自己的样式；否则继承父级样式。
样式按整体替换，不会逐字段合并。

## 自己试试

再创建一个使用不同变换的 Drawing，得到第三个实例。
然后修改组件定义中端口的半径，重新运行，所有实例都会使用新定义。
Group 表示一个组合物件；遮挡仍由子物件顺序和画布的 draw 顺序决定，它不是 Layer 接口。

接口说明：{py:class}`pdl.Group`、{py:class}`pdl.Drawing`、{py:meth}`pdl.Drawing.child`。

---

[上一章：锚点与连接](08-anchors.md) · [下一章：自定义轮廓与曲线](10-paths.md)
