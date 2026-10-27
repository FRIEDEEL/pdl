# 7. 在局部坐标系里画图

假设你要画一个整体倾斜的小零件。与其重新计算每个坐标，不如给零件一个自己的坐标系。

```{literalinclude} ../../../examples/tutorial/geometry/local_coordinates.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![灰色世界坐标轴与蓝色局部坐标轴](../../../examples/output/tutorial/geometry/local_coordinates.svg)

[完整可运行示例](../../../examples/tutorial/geometry/local_coordinates.py)

灰色坐标轴属于世界坐标系，原点在画布左下角。
蓝色坐标系的原点放在世界坐标 `(25, 15)`，方向旋转了 30 度。
圆的局部圆心是 `(10, 0)`，因此落在蓝色 x 轴上；这里的坐标从蓝色原点开始量，
不是从画布左下角开始量。

`translate(...) @ rotate(...)` 中，**右边的矩阵先作用**：先旋转局部坐标，
再平移原点。`Entity(..., space=local)` 表示把图形放进这个坐标系。
还可以用 `local.child(Transform.translate(...))` 在其中创建下一级坐标系。

这一章讨论的都是 author 层：也就是你怎样安排物件，在画布适配和输出之前使用的坐标。
你不需要根据 SVG 内部向下的 y 轴修改自己的坐标。

## 点和位移

`local.point(10, 0)` 表示蓝色坐标系中的一个位置；
`local.vector(10, 0)` 表示沿蓝色 x 轴的一段位移。
平移坐标系会移动点，但不会改变位移向量。
如果不确定一个普通坐标对属于哪个坐标系，可以把显式的空间点传给 `move_to`。

`canvas.map(local, matrix)` 可以只为当前画布改写这个坐标系的放置。
它替换局部到父坐标系的矩阵，不是在原矩阵上额外叠加。
其他画布和原坐标系本身都不会改变。

## 自己试试

把 `rotate(30)` 改成 `rotate(60)`，圆仍然在蓝色 x 轴上。
再把圆心从 `(10, 0)` 改成 `(10, 5)`，圆会沿局部 y 方向离开这条轴。

接口说明：{py:class}`pdl.CoordinateSystem`、{py:class}`pdl.SpacePoint`、
{py:class}`pdl.SpaceVector`。详细约定见[坐标专题](../../coordinates_zh.md)。

---

[上一章：移动、旋转和缩放](06-transforms.md) · [下一章：锚点与连接](08-anchors.md)
