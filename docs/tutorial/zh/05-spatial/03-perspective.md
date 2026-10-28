# 5.3 透视投影

保持三维构建不变，只替换相机。透视会让靠近相机的部分变大。第一行对比同一平面上的
底板、文字和下划线；第二行对比同一个 D10。正交原图保留在结果旁边，便于比较。

```{literalinclude} ../../../../examples/tutorial/spatial/perspective.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![平面图案与 D10 的正交和透视对比](../../../../examples/output/tutorial/spatial/perspective.svg)

[完整可运行源码](../../../../examples/tutorial/spatial/perspective.py)

## 位置与尺度

`PerspectiveCamera` 沿用 `OrthographicCamera` 的方位角、仰角和 target：世界 +z 向上，
方位角从 +x 朝 +y 计算，仰角从 xy 平面向上计算。以下距离单位都是毫米。

- `distance=100`：沿相机轴线，从相机位置到 target 的距离。
- `focal_length=100`：从相机位置到虚拟成像平面的距离。
- `near=0.1`：相机前方沿轴线允许的最小距离。

三者必须有限且为正，并满足 `near < distance`。target 投影到 `(0, 0)`；通过 target、
垂直相机轴线的平面，其比例为 `focal_length / distance`。两者相等时，该平面的比例为 1。
同时等比例增大两者，会保持该比例并减弱透视；只增大焦距则会放大图形。

对于世界坐标点，用相对 target 的相机向右、向上坐标记为 `x`、`y`，朝相机方向坐标记为 `d`：

```text
axial_distance = distance - d
projected_x = focal_length * x / axial_distance
projected_y = focal_length * y / axial_distance
```

`d` 越大越靠近相机。中心排序模式采用这个轴向深度，不是到相机的欧氏距离，也与光照方向无关。
`camera.eye` 返回世界坐标中的相机位置。`projected.point(...)`、`vertex(...)` 和
`face_center(...)` 使用同一投影；索引仍对应原始几何。

## 面内图案与二维标注

`Scene3D.project()` 仍只捕获二维 Authoring 快照，不测量文字。之后 Canvas 在自己的字体
配置下完成面内布局，再将字形轮廓和几何进行透视映射。因此，透视面内文字输出为矢量路径，
不再是可搜索的原生文字。直线精确投影；贝塞尔曲线、圆和字形轮廓转为折线，投影控制包络
相对折线段的偏差限制为局部投影尺度下 0.02 mm。外部二维缩放也会缩放这一容差。不生成位图。

描边宽度仍使用 Canvas 宽度，不模拟近粗远细的笔画。当前支持可转为路径的图形、Text、
单色 TeX 轮廓及其组合，填充限纯色；不支持渐变和嵌入图片。TeX 轮廓沿用现有 TeX 工具要求。
图案需要自行控制在面内，不自动按面的边界裁切。

legend 按[相关章节](01-projection.md)在投影后添加，保持普通二维内容，可继续输出原生文字。
修改源对象或相机后需要重新 `project()`；已有快照不追随修改。

## 本阶段限制

透视仅支持多面体和平面图案；Sphere、Cylinder 仍要求 OrthographicCamera，使用透视相机
会明确报错。所有顶点、图案端点和贝塞尔控制点都必须严格位于近裁面前方的有效空间。
无效多面体点在投影时报错，延迟图案可能在测量边界或导出时报错。不自动做近／远裁切。
本章带图案示例显式使用近似中心排序；纯多面体的 BSP 切分见[相关章节](05-visibility.md)。

试着将 distance 和 focal_length 同时从 55 改为 110：平面更接近左侧正交原图，target
平面的比例保持不变。


---

[本篇目录](index.md)
