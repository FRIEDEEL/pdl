# 26. 相交面与可见性

完整的一张面不一定能始终画在另一张面的前面或后面。两块相交板在交线两侧会交换
前后关系，中心深度或最大深度都无法表达这种变化。保留中心排序参照，直接比较：

```{literalinclude} ../../../examples/tutorial/spatial/visibility.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![同样的相交板：中心排序与 BSP 可见性](../../../examples/output/tutorial/spatial/visibility.svg)

[完整可运行源码](../../../examples/tutorial/spatial/visibility.py)

## 从三维片段到二维 Authoring

`Scene3D.project()` 默认 `visibility="auto"`。当场景中所有对象都是不带面内图案的
Polyhedron 时，使用 BSP（空间二叉划分）：

1. 选择一个面的支撑平面，将其他面按所在半空间分类。
2. 将跨越该平面的多边形切成片段，递归处理两侧。
3. 相对相机按远侧、共面面片、近侧的顺序遍历。
4. 将有序片段投影为普通二维 Authoring 绘图对象。

正交和透视相机都适用。简单凹面按需先三角化；凸面保持完整，直到需要切分。
三角化和 BSP 新增的边不描线。共面重叠按对象、面输入顺序决定优先级，后者在上；
不剔除背面。

投影后仍照常添加图例、引线和布局。顶点与面中心查询保持原始索引；
`projected.source_faces` 将当前每个绘制子项映射到 `(对象索引, 原始面索引)`，
同一源面可能对应多个片段。`reordered()` 同时重排这张映射，并将结果的
`visibility` 标记为 `"manual"`。

## 相交、循环与透明度

BSP 可以处理相交面，也可以处理不同重叠区域中 A 挡 B、B 挡 C、C 挡 A 的循环。
即使面在空间中不相交，也可能形成后者；切分后的小片段可以获得有效绘制顺序。
`Polyhedron.opacity` 仍是逐面／片段从远到近合成，不模拟折射玻璃，也不生成布尔实体。

[较大的完整示例](../../../examples/spatial/visibility.py) 包含平行面排序错误、
相交面、三个条带的循环遮挡与透明相交面：

![四组中心排序与 BSP 对照](../../../examples/output/spatial/visibility.svg)

## 明确的边界与安全预算

- `visibility="bsp"` 要求支持的纯多面体场景；遇到球、圆柱、自由 Plane3D 图案或
  面内图案直接报错。
- `"auto"` 在这些场景中选择**整个场景的近似中心排序**并发出提示。
  确实接受该近似时写 `visibility="centroid"`；`projected.visibility` 报告实际模式。
- `sort_faces=False` 无论 visibility 如何都不排序、不切分。整面手动重排不能解决循环。
- `bsp_tolerance=1e-8` 是以毫米为单位的有限正**世界空间绝对平面容差**。
  这是浮点计算，不是精确谓词；极小间隔可能视为共面。极端尺度应调整几何或容差。
  跨越相机近面的对象仍报错，不自动裁切。
- `max_fragments=100000` 包括三角化及 BSP 片段。超出预算或内部树深 500 时明确报错，
  不退回近似算法。支撑平面无限大，可能切分实际不相交的有限面；稠密输入可能产生
  大量片段并增加输出耗时。

[上一章：透明度与深度顺序](25-depth-order.md)

[下一章：圆柱曲面](27-cylinder-surfaces.md)
