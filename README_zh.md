# pdl — Python Drawing Library

pdl 用 Python 对象构建静态矢量图，包括 2D 形状和路径、Unicode 文字与 TeX、可复用组件、
图示连接及 3D 形体投影。SVG 与 TikZ/PDF 共用同一 Author 领域模型，需要 Python 3.12+。

[English](README.md) · [中文教程](docs/tutorial/zh/index.md) ·
[API 参考](docs/api/index.md) · [架构](docs/architecture_zh.md)

## 绘制与保存

在仓库中通过 pyenv 选择 Python，运行 `uv sync` 安装。SVG 需要可用字体；
TeX 测量需要 XeLaTeX 和 dvisvgm，原生字体 PDF 输出需要 XeLaTeX 及相应 LaTeX 包。

```python
from pdl import Canvas, Color, Group, Style, circle, line, text

disk = circle((20, 25), 10, style=Style(fill=Color(0.7, 0.85, 1)))
connector = line((35, 10), (70, 35), style=Style(line_width=0.5))
label = text("A reusable component", position=(12, 45), size=11)
component = Group(disk, connector, label)
canvas = Canvas(80, 55).add(component)
canvas.save("drawing.svg")
canvas.save("drawing.tex", backend="tikz", tikz_mode="pdf")
```

`circle`、`rectangle`、`text` 等绘图工厂返回 Entity。纯 `Path` 等描述从
`pdl.author.geometry` 导入，Entity 结合样式与绘图操作。Canvas.add／draw 捕获当前状态，
之后的修改需要再次提交。

几何描述继承 `pdl.author.geometry` 中的 `Geometry`。这个基类只表达类型归属，
不要求共同操作；传入 Entity 的自定义描述也需要继承它。
路径转换仍是独立的可选能力，可用于后端输出兜底。

## 显式导入所需能力

根入口仅提供绘图工厂、Entity、Group、Gather、Canvas、Style 和 Color，其他能力从所属包导入：

```python
from pdl.author.geometry import Path, Point
from pdl.author.style import Font, LinearGradient
from pdl.author.transform import Rotation
from pdl.canvas import Layer, Query
from pdl.extensions.diagram import Node
from pdl.extensions.spatial import Scene3D, PerspectiveCamera
```

需要显式构造几何描述时再引入 Geometry；3D 和图示各自提供独立的公开入口，按需加载。

## Author 行为

- Geometry 保存当前坐标与形状参数；Entity 直接持有几何及可选 Style，并提供参考点、中心和锚点查询。
- Entity 方法立即编辑并返回自身。拉伸圆可转成 Path 几何，Entity 身份保持不变；对象不保存累计变换或隐式局部坐标系。
- 默认旋转／缩放围绕参考点：圆心、矩形原点、路径首个 Move、文字基线，或显式 Group 参考点。
  可用 origin 指定其他支点，set_reference 改变后续默认支点。
- 默认线宽不变；均匀 rescale 可显式包含线宽，非均匀缩放不提供此选项。
- Entity.style None 保持未设置，按显式 Group 样式及默认值回退。
  Group.set_style 只改 Group；Gather(*group.members).set_style 显式统一修改成员。
- Group 是有单父级归属的 Entity；Gather 是可重叠的身份选择；Layer 属于 Canvas，控制覆盖顺序。
- 世界坐标采用毫米，x 向右、y 向上。显式 Frame 提供数值转换，frame_axes 创建可绘制坐标轴。
- 文字／TeX 按需测量，字号使用 TeX point。普通 Text 在保持朝向手性的相似变换下保留原生描述；
  TeX 平移／旋转保留源码，缩放则变换已测量的轮廓。其他变形也不可逆地转路径，不支持的复杂 TeX 轮廓会报错。
- Canvas 捕获几何、有效样式、排版与顺序，后端直接编码这些 Entity，不建立第二套场景模型。

需要保留可编辑版本时调用 copy。允许显式共享可变几何：直接几何编辑会影响共享者，
Entity 变换仅替换目标持有的几何。参见[复制与捕获](docs/tutorial/zh/02-shapes/03-copy-and-capture.md)。

## 组件与 3D

用参数化 Python 函数或 Entity／Group 子类构建自己的组件库，组合形状、查询当前锚点，再提交 Group。
位置查询返回固定数字，后续编辑不建立持续约束，也不会自动重画依赖连接。

Scene3D.project 产生 2D ProjectedScene Group，支持正交／透视相机、索引多面体、平面图案、
平滑圆柱表面、光照和 BSP 可见性。曲面／带图案场景采用已说明的 centroid 限制。
独立投影组件的覆盖遵循普通 Canvas 顺序。

[examples](examples) 保留 geometry、composition、text、diagrams、coordinates、spatial 和七部分教程的组织。
生成输出按来源路径镜像到 examples/output，不纳入 Git。

## 构建与验证

```sh
uv run ruff check .
uv run ruff format --check .
uv run pyright
uv run pytest
uv run python -m examples.tutorial.render_all
uv run python -m examples.tools.render_all --tikz-mode pdf
uv run --group docs python docs/build.py
uv build
```

打开 docs/_build/html/index.html 选择中文或英文。两种语言的导航和搜索独立，
对应页面之间提供语言切换链接。文档构建通过可运行源码生成实际插图。
工具配置见[构建指南](docs/building.md)，不兼容变化见[迁移说明](CHANGELOG.md)。
原生字体在 SVG 查看器与 LaTeX 中可能呈现不同像素。
非线性／网格变换、自动避障、独立组透明合成与实体布尔运算仍待后续工作。
