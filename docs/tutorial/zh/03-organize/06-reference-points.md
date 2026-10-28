# 3.6 不绘制的参考点

`ReferencePoint` 是定位或指定支点的 Entity，可以移动、复制、加入 Group 或 Gather。
它不产生绘制内容，不计入可见边界、画布自动适配，也不参与遮挡。

```{literalinclude} ../../../../examples/tutorial/layout/reference_points.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![矩形围绕标出的参考点旋转](../../../../examples/output/tutorial/layout/reference_points.svg)

[完整源码](../../../../examples/tutorial/layout/reference_points.py)

`pivot.position` 是当前世界位置的数值。红色标记是显式创建的 Circle，
不是参考点自动画出来的内容。灰色轮廓保留原矩形以供对比。

单独移动矩形不会移动参考点；需要共同操作时使用 `Gather(box, pivot)`。
Frame 则在一个原点之外增加两个基矢，下一节说明。

[本篇目录](index.md)
