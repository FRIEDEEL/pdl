# 简单三维绘图

在右手三维坐标系中定义图形，再投影到普通二维 `Canvas`。长度单位是毫米，
旋转角度使用度数和右手定则。SVG 与 TikZ 共用投影后的多边形和面颜色，无新增运行时依赖。

## 多面体、相机与光源

```python
from pdl import (
    Canvas,
    Color,
    DirectionalLight,
    OrthographicCamera,
    Scene3D,
    Vector3D,
    regular_polyhedron,
)

solid = regular_polyhedron("dodecahedron", radius=20, color=Color(0.38, 0.73, 0.91))
scene = Scene3D(
    (solid,),
    camera=OrthographicCamera(azimuth=30, elevation=22),
    light=DirectionalLight(direction=Vector3D(-1, 1, -2), ambient=0.22),
)
canvas = Canvas(60, 60, mode="fit", padding=5)
canvas.draw(scene)
canvas.save("solid.svg")
```

`regular_polyhedron` 支持全部五种正多面体：`tetrahedron`（正四面体）、
`cube`（正六面体）、`octahedron`（正八面体）、`dodecahedron`（正十二面体）、
`icosahedron`（正二十面体）。`radius` 是正的**外接球半径**，不是边长。

自定义 `Polyhedron(vertices, faces)` 使用顶点和面索引。每个面必须是简单、凸、共面的
多边形，顶点从外侧看按逆时针排列，绕序决定法向。不检查整体拓扑或面之间的相交。
`face_colors` 可以逐面指定固有色。`transformed()` 返回新多面体，镜像时保持向外绕序，
变换后的顶点用于重新计算法向，因此支持非均匀缩放。

正交相机朝向 `target`，目标投影为 `(0, 0)`。世界 +z 向上，方位角由 +x 转向 +y，
仰角从 xy 平面向上计算。默认角度是等轴测视角。投影保留毫米尺度，可通过二维
`Drawing`／`Transform` 放置整个场景，或使用画布适配。普通二维标注可直接叠加。

光源 `direction` 是世界坐标中的**光传播方向**。设 `n` 和 `d` 为归一化面法向与光方向：

```text
intensity = ambient + (1 - ambient) * max(0, -dot(n, d))
face_rgb = intrinsic_rgb * intensity
```

正对光源的面保留完整固有色，垂直于光线或背光的面只保留环境光。
`ambient` 范围为 `[0, 1]`，默认为 `0.25`。方向向量长度不影响亮度，移动相机不改变光照。
这是直接作用于 RGB 通道的示意图映射，不做伽马转换、投影阴影、高光或距离衰减。
设置 `Scene3D(light=None)` 可保留未调制的固有色。

## 全部五种正多面体

运行 `uv run python -m examples.spatial.platonic_solids`，SVG、TikZ 源码和 PDF
写入 `examples/output/spatial/platonic_solids.*`。修改脚本顶部的 `CAMERA`、`LIGHT`
和 `BASE_COLOR` 可比较视角与光照。

```{literalinclude} ../examples/spatial/platonic_solids.py
:language: python
```

![五种正多面体](../examples/output/spatial/platonic_solids.svg)

## 坐标系与三维平面

`Transform3D` 支持平移、均匀／非均匀缩放、绕任意轴旋转、复合与求逆；
`a @ b` 先作用 b。奇异变换允许正向映射，但不能求逆；塌缩的面会被拒绝。
`CoordinateSystem3D.child()` 建立嵌套不可变坐标系，`convert_point()` 包含平移，
`convert_vector()` 忽略平移。这些坐标系独立于二维坐标系和 Canvas 映射；
构造场景几何前，先将坐标转换到三维世界空间。

`Plane3D(origin, u, v)` 将局部 `(x, y)` 映射成 `origin + x*u + y*v`。
两个基向量需线性无关，可以不正交、不归一化，法向为归一化 `u.cross(v)`。
无限平面本身不绘制，`plane.place(graphic, style)` 将有限二维图形、组或标签放到平面上。
投影是仿射映射，圆会变成椭圆，文字随平面变形。`Canvas.draw()` 会捕获场景内的
内置可变 Path／Entity 状态，与二维语义一致。

平面图案保留自身样式。需要受光的底板时，用 `light.shade(固有色, plane.normal)`
显式指定填充色，子图案不会被统一改色。平面图案作为一个整体参与深度排序，默认以
平面原点为参考，也可用局部 `depth_point=(x, y)` 指定；内部二维绘制顺序保持不变。

运行 `uv run python -m examples.spatial.planes` 可查看倾斜平面，以及通过嵌套坐标系
转换位置的标记点。

```{literalinclude} ../examples/spatial/planes.py
:language: python
```

![Plane placement](../examples/output/spatial/planes.svg)

## 遮挡边界

同一个 `Scene3D` 中，所有多面体的面统一按面中心深度从远到近排序，同深度保持输入顺序。
平面图案使用其指定参考点。不同场景之间仍遵循 Canvas 绘制顺序。

不切割相交面，不解决循环遮挡；深度区间重叠时排序可能出错。暂不提供自动隐藏边虚线、
透明遮挡求解、透视、背面剔除或几何裁切。当前主要面向封闭、不透明的凸多面体。
需要手动控制时，设置 `sort_faces=False`，自行排列对象与面。
