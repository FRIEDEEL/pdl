# 3.8 挂接物件与连接节点

如果不知道一个标签有多宽，不必猜它的边缘坐标。
可以引用物件上有名字的点，也就是**锚点**：`east` 在右边，`west` 在左边，
`north` 在顶部，`center` 在中间。

## 连接两个标签

```{literalinclude} ../../../../examples/tutorial/layout/anchors.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![通过边缘锚点连接的两个节点](../../../../examples/output/tutorial/layout/anchors.svg)

[完整可运行示例](../../../../examples/tutorial/layout/anchors.py)

Finish 的中心位于 Start 的右侧锚点向右 35 mm 的地方。
这里是到中心的偏移，不是两个外框之间留出 35 mm 空隙。
连线从 east 接到 west；红色辅助点标出两个端点。
Connection 默认在末端加箭头；`arrow_end=False` 可以取消箭头，
`via=((x, y), ...)` 可以指定中间途经点，但不会自动绕开其他物件。

渲染时才测量节点的文字和尺寸，所以写场景时不用提前求宽度，连线也能接在正确的边缘。
先画连线、后画节点，可以让连线位于节点后方。

## 移动物件后，原来的挂接会怎样？

```{literalinclude} ../../../../examples/tutorial/layout/captured_anchors.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![旧挂接留在下方，新挂接使用移动后的矩形](../../../../examples/output/tutorial/layout/captured_anchors.svg)

[完整可运行示例](../../../../examples/tutorial/layout/captured_anchors.py)

橙色圆在矩形移动前挂上，所以保留原来的位置；绿色圆在移动后挂上，使用新位置。
Entity 的 anchor 捕获的是**调用时的状态描述**，不会继续跟随这个 Entity 后来的编辑。

这里还没有把描述变成固定的数值点。如果位置依赖文字度量，更换渲染字体仍可能改变它。
如果希望一组互相连接的物件一起变换，可以用下一章的 Group。

对于旋转后的物件，east 表示局部右侧锚点随物件变换后的结果，
不一定是最终轴对齐包围盒的最右点。
需要明确偏移方向时，可以写 `anchor.shifted(frame.vector(...))`，指定沿哪个坐标系偏移。

## 自己试试

把 Start 的文字改成 `"A longer starting label"`。
右侧节点和连线会依据重新测量的右边缘调整；必要时加宽画布。

接口说明：{py:class}`pdl.AnchorRef`、{py:class}`pdl.Connection`、{py:meth}`pdl.Entity.anchor`。


---

[本篇目录](index.md)
