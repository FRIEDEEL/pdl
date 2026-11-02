# 3D 组件、投影和可见性

Point3D、Vector3D、Transform3D 使用右手毫米坐标，普通 3D 变换返回新形体。
Polyhedron 保存顶点和有序面环，支持规则多面体、凹面环、面颜色和透明度；表面需要简单、共面、非退化的面环。
Plane3D 用原点及两个基向量承载 2D 图案，face_plane 为索引面提供坐标图。

Scene3D.project 明确产生一个可编辑 2D ProjectedScene Group，再交给 Canvas。
vertex／face_center／point 查询返回当前投影数值，随后续 2D 编辑一起变化，不改写源 3D 场景。
投影图案中的普通 Text 在保持朝向手性的相似变换下保留原生表达；TeX 平移／旋转保留源码，
缩放及其他变形立即转换已测量的轮廓。图案不自动裁剪或受光。

OrthographicCamera 保留毫米比例；PerspectiveCamera 提供针孔投影，near 边界处直接拒绝，不自动裁剪。
透视平面的曲线和字形通过受限误差的路径细分表达；图片和曲面体使用受支持的正交流程。
DirectionalLight 提供简单的方向面色映射，不计算阴影或物理光传输。

visibility="auto" 对无图案的多面体选择 BSP，拆分相交面并保留源面索引，新切割边不描边。
不支持的对象回退 centroid 并警告；显式 bsp 会拒绝不支持场景，显式 centroid 接受近似排序。
sort_faces=False 保留输入顺序。算法使用浮点容差、片段预算和树深限制，不提供实体布尔运算。

Sphere、Cylinder、CylinderSurface、AnnularCylinder 通过平滑路径与渐变表达正交图示。
曲面采用 centroid／manual 排序，变换遵循各类的相似变换限制。独立投影只通过 Canvas 顺序组合，
不共享 BSP 或深度缓冲。需要独立覆盖顺序时显式分组件投影，并保留参照视图以检查效果。


![五种正多面体](../examples/output/spatial/platonic_solids.svg)

![Plane placement](../examples/output/spatial/planes.svg)

![D10 面图案与二维标注](../examples/output/spatial/d10.svg)

![光滑曲面](../examples/output/spatial/curved_solids.svg)

![圆柱视角检查](../examples/output/spatial/curved_solids-views.svg)

[3D 教程](tutorial/zh/05-spatial/index.md) · [API](api/spatial.md) · [English](spatial.md)
