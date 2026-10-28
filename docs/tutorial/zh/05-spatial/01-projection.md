# 5.1 先投影三维，再绘制二维

三维场景决定相机与光源。调用 `project()` 得到二维 Authoring 快照，再组合普通二维绘图对象，
最后让 Canvas 统一求值。这个快照不是渲染图片，也不是 Resolved 结果。

```{literalinclude} ../../../../examples/tutorial/spatial/projection.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![投影立方体与二维标注](../../../../examples/output/tutorial/spatial/projection.svg)

[完整可运行示例](../../../../examples/tutorial/spatial/projection.py)

`regular_polyhedron` 的半径是毫米单位的外接球半径。正交相机方位角从世界 +x 转向 +y，
仰角从 xy 平面向上计算，世界 +z 向上。投影保留长度尺度，不产生随距离改变大小的透视效果。
面的颜色采用场景平行光与环境光计算。

`projected.vertex(0, 7)` 对应源对象 0 的顶点 7，面排序不改变这些索引。
返回值是固定的局部二维点。引线与 legend 在投影后创建，因此文字保持在绘图平面内。
最后的 Group 旋转会一起作用于投影、引线和标注；如果只变换投影对象，这些固定坐标不会自动跟随。

投影捕获源场景中的内置可变 Path／Entity，但不测量文字；字体相关布局与边界留到 Canvas
求值时确定。修改视角或源对象需要再次 `project()`，旧快照不更新。
`point(Point3D(...))` 用同一相机投影任意世界坐标点，
`face_center(对象索引, 面索引)` 返回投影后的面顶点平均位置。这些方法不判断可见性。
`projected.anchor()` 则提供前面章节使用的普通数值边界锚点。

流程为 **3D 扩展 → 2D Author 与标注 → Canvas 捕获 → 后端**。
组合二维标注时使用显式投影。
纯多面体场景采用 BSP 切分处理相交与循环；图案和曲面的显式近似模式及可见性流程
见[相关章节](05-visibility.md)。

试着修改相机仰角并重新运行，再改变整个 Group 的二维旋转角度，观察标注如何一起移动。


---

[本篇目录](index.md)
