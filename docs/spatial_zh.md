# 简单三维绘图

在右手三维坐标系中定义图形，再投影到普通二维 `Canvas`。长度单位是毫米，
旋转角度使用度数和右手定则。SVG 与 TikZ 共用投影后的多边形和面颜色，无新增运行时依赖。

## Authoring 投影边界

`scene.project()` 显式返回 `ProjectedScene`，它是普通二维 Authoring 组合对象。
投影捕获内置可变描述，固定本次相机、光照、几何和深度顺序，但不测量文字、不执行二维布局。
在结果上组合 legend、辅助线、引线，再交由 Canvas 将整套二维 Authoring 求值到 Resolved，
最后输出 SVG／TikZ。

`projected.vertex(对象索引, 顶点索引)`、`face_center(对象索引, 面索引)` 和
`point(世界三维点)` 返回固定的**局部二维毫米坐标**；索引保持原始输入顺序，不随面排序改变。
它们不是可见性查询，也不是跟随已移动实例的引用。把投影与标注放进同一个 Group，便可一起
变换。改变视角时重新 project，旧结果不变。`projected.anchor()` 提供普通延迟边界锚点。
非多面体对象没有顶点／面数据。

旧的 `canvas.draw(scene)` 保留为相同投影路径的兼容简写；新代码推荐显式 project。

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
canvas.draw(scene.project())
canvas.save("solid.svg")
```

`regular_polyhedron` 支持全部五种正多面体：`tetrahedron`（正四面体）、
`cube`（正六面体）、`octahedron`（正八面体）、`dodecahedron`（正十二面体）、
`icosahedron`（正二十面体）。`radius` 是正的**外接球半径**，不是边长。

自定义 `Polyhedron(vertices, faces)` 使用顶点和面索引。每个面必须是简单、共面的
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

## 面内图案与 D10 示例

`solid.face_plane(i)` 返回以该面顶点平均位置为原点的单位坐标图。局部 v 朝向世界 +z
在面内的投影，水平面则用第一条边作为 u。
`solid.with_face_artwork(i, graphic, style=None, transform=Transform())`
返回替换了第 i 面图案的新多面体。图案可以是 Text、Path 或 Group，不要求栅格贴图。

图案在 project 时捕获，与对应面一起排序，使用完整平面仿射变换；文字测量仍留在后续二维
求值阶段。图案是单面的，背向观察者或侧立时省略；不自动受光，不裁切到面边界，需要控制在
面内部并显式指定文字样式。整体三维变换会传递图案的位置，包括缩放与镜像。

[D10 示例](../examples/spatial/d10.py) 用 12 个顶点和 10 个平面风筝形 loop 构造五方偏方面体，
生成 1–10 的居中数字图案，再投影成两个相反视角，并添加二维标注。D10 只是示例，
不增加专用库图元，也不规定骰子编号惯例。本轮不增加半空间构造器或一般布尔合并。

![D10 面图案与二维标注](../examples/output/spatial/d10.svg)

对应教程：[21](tutorial/zh/21-project-3d.md)、[22](tutorial/zh/22-plane-artwork.md)、
[23](tutorial/zh/23-d10.md)。

## 光滑圆柱与球面

`Cylinder(base=Point3D(...), radius=10, height=25, axis=Vector3D(0, 0, 1))`
定义封闭圆柱，base 是底面圆心，height 是正的轴向高度，非零 axis 从底面指向顶面，
向量长度不影响结果。`Sphere(center=Point3D(...), radius=10)` 定义球体。
两者都接受固有色 `color`、轮廓色 `stroke`（可设为 `None`）和 Canvas 毫米线宽
`line_width`。尺寸必须有限且为正，直接加入 `Scene3D.objects` 即可。
圆柱通过 axis 定向，暂不支持一般仿射变换后的椭球。

两者采用**连续矢量渐变，不使用曲面分片**：

- 圆柱侧面是一个曲边区域，沿投影宽度取 33 个色标，按真实世界法向计算 Lambert
  亮度，再用线性渐变插值，沿轴向保持同色。朝向观察者的端面是单色椭圆；
  沿轴观察时只画端面圆，纯侧视时不画退化端面。
- 球面是一个圆，填充径向渐变。设相机坐标中的朝向光源单位向量为 `(sx, sy, sz)`，
  `l = sqrt(sx² + sy²)`。归一化渐变中心为
  `(0.5 + 0.35*sx, 0.5 + 0.35*sy)`，半径为 `0.5 + 0.15*l`；
  `sz >= 0` 时漫反射峰值为 1，否则为 l。亮区到环境光边界用 33 个色标采样
  `(1 + cos(pi*t))/2`，得到平缓过渡。这是**视觉近似，不逐点满足 Lambert 公式**。
  光源正处于背面时只保留环境光。

`light=None` 时使用固有色纯色填充。SVG 使用原生线性／径向渐变，TikZ／PDF
复用已有函数式 shading，使用相同色标、变换和直接 RGB 插值。曲边通过三次贝塞尔
圆弧近似，不需要栅格填充、SVG 光照滤镜或渐变网格。
球和圆柱都按中心深度整体排序，不与其他物体的表面交错排序；面相交与循环遮挡限制仍然适用。

运行 `uv run python -m examples.spatial.curved_solids`，生成不同光方向和圆柱特殊视角的
SVG、TikZ 与 PDF 对比图。

![光滑曲面](../examples/output/spatial/curved_solids.svg)

![圆柱视角检查](../examples/output/spatial/curved_solids-views.svg)

```{literalinclude} ../examples/spatial/curved_solids.py
:language: python
```

## 遮挡边界

同一个 `Scene3D` 中，所有多面体的面统一按面中心深度从远到近排序，同深度保持输入顺序。
平面图案使用其指定参考点。不同场景之间仍遵循 Canvas 绘制顺序。

不切割相交面，不解决循环遮挡；深度区间重叠时排序可能出错。暂不提供自动隐藏边虚线、
透明遮挡求解、透视、背面剔除或几何裁切。当前主要面向封闭、不透明的凸多面体。
需要手动控制时，设置 `sort_faces=False`，自行排列对象与面。
