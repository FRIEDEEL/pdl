# 27. 圆柱曲面

先画圆柱形材料的后半部分，让开口朝向观察者。这里需要一张平滑的弯曲侧壁，
上下保持开放，下一章再放入 probe。

```{literalinclude} ../../../examples/tutorial/spatial/cylinder_surface.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![从内部观察开放的半圆柱面](../../../examples/output/tutorial/spatial/cylinder_surface.svg)

[完整可运行源码](../../../examples/tutorial/spatial/cylinder_surface.py)

## 在世界坐标中选择开口

`CylinderSurface` 只有弯曲侧面，没有厚度、端盖或平直切面。尺寸和位置使用毫米。
`base` 是底圆圆心，`height` 沿归一化后的 `axis` 方向延伸。

`radial` 定义零度方向，必须垂直于 `axis`，长度忽略。默认轴为 +z、零度方向为 +x，
正角度朝 +y 旋转。因此 `start_angle=90, sweep_angle=180` 保留 x ≤ 0 的一半；
方位角为 0 的相机从 +x 看进开口。默认角度范围为 0–180°，请根据所需开口明确设置。
扫角必须为正，最大 360°。曲面两侧使用同一种纯色，不随场景光照改变。

`sort_faces=False` 选择手动对象顺序。曲面内部仍先画远侧分支、再画近侧分支，
仅在正交投影的轮廓处拆开。圆弧用每段不超过 45° 的三次 Bézier 曲线近似，轴向边为直线，
不生成多边形网格。完整 360° 侧面没有人为的接缝线。BSP 不处理这种曲面。

## 垫圈有侧壁和端盖

垫圈是带轴向孔洞的封闭实体，与开放的侧面不同：

```{literalinclude} ../../../examples/tutorial/spatial/washer.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![中央孔洞保持开放的垫圈](../../../examples/output/tutorial/spatial/washer.svg)

[完整可运行源码](../../../examples/tutorial/spatial/washer.py)

`AnnularCylinder` 要求 `0 < inner_radius < outer_radius`，高度为正。
投影按顺序绘制可见内壁、外壁和朝向观察者的环形端面。孔洞是空缺的几何，
不是白色圆盘：没有被侧壁或端面挡住的位置，可以看到先前绘制的内容。

![垫圈和开放曲面的俯视、仰视、侧视与沿轴视图](../../../examples/output/spatial/material_probe-views.svg)

橙色线先于各个垫圈绘制。视角允许时，线能穿过孔洞显露；纯侧视时则被外壁挡住。
下排展示同样相机角度下的开放半圆柱面。

## 在投影前修改几何

两个类型均不可变。用 `dataclasses.replace` 修改尺寸、底圆圆心或轴向，或用
`.transformed(Transform3D...)` 获得平移、旋转、镜像或均匀缩放后的副本。
曲面的 `point(angle, height)` 返回世界坐标，可用于附着对象或标注。
角度单位为度，高度为轴向毫米；该查询不判断可见性，也不限制在曲面的角度和高度范围内。

非均匀缩放、剪切和奇异变换会报错，因为它们不能保持圆柱形状。
`axis` 与 `radial` 必须保持垂直。

这些新类型与已有平滑 `Cylinder`、`Sphere` 一样，目前仅支持 **OrthographicCamera**。
使用 PerspectiveCamera 会明确报错。中心排序模式将它们作为整个对象处理，
不解决与其他对象的相交遮挡。自动模式会警告并让整个场景使用中心排序；
显式 BSP 模式拒绝曲面。需要人为控制插图层次时，可以使用下一章的独立手动投影。

[上一章：相交面与可见性](26-visibility.md) · [下一章：投影图层](28-projected-layers.md)
