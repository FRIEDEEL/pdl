# pdl — Python Drawing Library

具体形状本身就是可编辑的 `Entity`：直接变换，需要留档时使用 `.copy()`。
`Frame` 和 `ReferencePoint` 是不绘制的参考对象；需要参考系随图形共同变换时，
显式使用 `Gather`。参见[对象与参考系教程](docs/tutorial/zh/29-entities-and-frames.md)。

一个用于静态矢量绘图的类型化 Python 库，支持几何图形、路径、文字、LaTeX 公式、
节点连接、组合复用和仿射坐标系，输出 SVG 或 TikZ。需要 Python 3.12 或更高版本。

[English](README.md) · [英文教程](docs/tutorial/en/index.md) ·
[中文教程](docs/tutorial/zh/index.md) · [API reference](docs/api/index.md)

## 阅读文档

在仓库根目录构建本地文档站：

```sh
uv sync --group docs
uv run --group docs sphinx-build -W --keep-going -b html docs docs/_build/html
```

用浏览器打开 `docs/_build/html/index.html`。构建会自动生成教程图片，
并直接从可运行示例中截取代码。完整构建需要可用的系统 sans-serif 字体、
XeLaTeX、dvisvgm，以及 LaTeX 的 standalone、amsmath 和 TikZ 包。
详见[构建说明](docs/building.md)。当前只配置本地站点，没有公开托管。

## 一个小例子

```python
from pdl import Canvas, Circle, Color, Path, Style

canvas = Canvas(80, 50)
canvas.draw(Circle((20, 25), 10), Style(fill=Color(0.7, 0.85, 1)))
curve = Path().move_to((35, 10)).cubic_to((40, 45), (65, 45), (70, 10))
canvas.draw(curve, Style(line_width=0.5))
canvas.save("drawing.svg", backend="svg")
canvas.save("drawing.tex", backend="tikz")
```

## 坐标与绘制约定

- 坐标、几何尺寸和线宽以毫米为单位。默认固定视口的原点在左下角，x 向右、y 向上，
  超出视口的内容被裁剪。角度以度为单位，逆时针为正。
- Point 是坐标值，不是可绘制图形，也可以直接传入坐标对。
- Line、Polyline、Circle、Rectangle、Polygon、Arc、Path 描述几何，
  Style 描述外观，Canvas.draw 把物件加入绘制列表。
- 普通几何的默认样式为黑色描边、线宽 1 mm、不填充、butt 线端、miter 拐角，
  miter limit 为 10。RGB 各分量在 0 到 1 之间。
- 图层从下向上绘制，同层后加入的物件画在前面。后端尽量保留原生图形，不支持时再通过 to_path 等方式拆解。
- Path 是可变构造器。draw 捕获当时的命令，后续修改需要再次 draw；
  path.to_path() 可以取得独立副本。
- Path 支持绝对坐标的 move_to、line_to、quadratic_to、cubic_to、arc、close。
  二次贝塞尔曲线有一个控制点，三次曲线有两个。
- close 闭合当前子路径，并把当前点返回起点。填充会隐式闭合开放子路径，
  但描边不会自动补上闭合边。填充规则支持默认 nonzero 和 evenodd。
- 两个后端都不绘制零线宽描边。无效值抛出普通 Python 异常，没有自定义异常层次。

## 圆弧

标准形式是 `Arc(center, radius_x, radius_y, start_angle, sweep_angle, rotation=0)`。
半径必须为正，带符号跨度的绝对值不超过 360 度。另外提供两种参数形式：

```python
from pdl import Arc

arc = Arc.from_tikz((10, 20), radius=8, start_angle=90, end_angle=270)
arc = Arc.from_svg(
    (10, 20),
    (30, 25),
    radius_x=15,
    radius_y=8,
    rotation=20,
    large_arc=False,
    sweep=True,
)
```

from_tikz 的位置是圆弧起点，可用 radius_y 指定椭圆。
from_svg 使用 SVG 端点换算和半径修正，但坐标仍是笛卡尔方向，sweep=True 表示角度递增，
视觉上逆时针。负输入半径取绝对值，零半径返回 Line，重合端点返回只移动的 Path。
完整圆应使用标准构造或角度构造，不能用重合的 SVG 端点表示。

SVG 保留原生椭圆弧；TikZ 保留未旋转的原生圆弧，旋转圆弧回退为三次曲线。
Arc.to_path 和 Path.arc 也使用每段不超过 45 度的三次曲线近似；
单位圆径向误差低于 5e-6，椭圆误差按较大半径缩放。
Circle 在两个后端都使用原生输出。TikZ 把二次曲线精确转换为三次曲线。
这里保证几何与外观语义的一致，不保证逐像素一致。

## 示例与开发

用 pyenv 选择 Python 后运行：

```sh
uv sync
uv run python -m examples.geometry.gallery
uv run python -m examples.tutorial.render_all
uv run ruff check .
uv run ruff format --check .
uv run pyright
uv run pytest
```

画廊输出在 `examples/output/geometry/`，教程输出在 `examples/output/tutorial/`，
均镜像源码目录。完整教程运行器还会编译其中的 TeX 示例。
TikZ 编译需要外部 TeX 环境、TikZ 和 standalone，它们不是 Python 运行时依赖。
测试检查几何、圆弧转换、路径、XML 结构、原生输出、回退和真实 TeX 编译；
缺少相关编译器时会显式跳过对应测试。示例仍需要视觉检查，目前没有像素基准套件。

尚未实现图层组、整组合成透明度、自动布局与布线、任意后端选项、动画和 3D。
发布前公共接口仍可能调整。捕获语义、锚点、变换和画布适配见教程与
[坐标专题](docs/coordinates_zh.md)。


## 组合、层序与图像

Group 是单一父级的空间组合，Gather 是可以跨层的扁平操作集合。
通过 Entity／Group 的 set_layer(int_or_layer) 分配图层；Layer 只控制覆盖顺序。
详见教程[第 16–18 章](docs/tutorial/zh/16-editable-groups.md)。

[图片](docs/tutorial/zh/19-images.md)使用显式毫米视口，支持 PNG／JPEG 和
contain／cover／stretch 适配。SVG 内嵌字节，导出 TikZ 后需要保留同级图片资源目录。
[渐变](docs/tutorial/zh/20-gradients.md)使用形状局部边界归一化坐标。
原生文字／TeX 仍限纯色；本阶段不含图层组与整组合成透明度。

三维多面体支持正交与[透视投影](docs/tutorial/zh/24-perspective.md)，纯多面体场景默认用 BSP 切分处理相交与循环遮挡（不含面内图案），另有显式近似模式；
保留背面并支持每面透明度，参见[透明度与手动顺序](docs/tutorial/zh/25-depth-order.md)。

多面体切分与模式边界见[相交面与可见性教程](docs/tutorial/zh/26-visibility.md)。

## 从组件搭建显微镜

运行 `uv run python -m examples.spatial.microscope`，导出整机与组件拆分图的
SVG、TikZ 和 PDF。[源码](examples/spatial/microscope.py)用参数化函数和具名嵌套
组合构建底座、支架、载物台、聚光器与光学组件。整机位置在 `make_microscope`
中调整，玻片细节见 `make_stage`，物镜和目镜见 `make_optics`。
示例内的 `Assembly` 是局部组合配方，不是公共 Group3D API。
圆形部件使用多面体近似，完整场景先用 BSP 处理遮挡，再生成二维绘图对象。

调焦机构细分为导轨、升降齿条／滑座、横向传动轴、示意小齿轮和带握纹的
粗细调焦轮；`make_focus_drive` 将齿条与载物台托架的升降关联。
额外导出 `microscope-focus`，用浅色简化旧结构对照打开近侧旋钮后的机构细节。
齿形和微调连接表达构造意图，不作为工程齿形或运动学规格。

## 圆柱材料与 probe 图层

`CylinderSurface` 表示开放半圆柱面，`AnnularCylinder` 表示封闭垫圈。
两者使用 OrthographicCamera，输出纯色、平滑矢量边界。
见[曲面教程](docs/tutorial/zh/27-cylinder-surfaces.md)与
[投影图层教程](docs/tutorial/zh/28-projected-layers.md)。

运行 `uv run python -m examples.spatial.material_probe` 生成
[材料／probe 剖面示意图](examples/spatial/material_probe.py)。
独立投影共用相机，之后按材料、内部截面、probe、标注的二维顺序绘制。
BSP 仅在每个受支持的多边形场景内处理，不计算独立快照之间的遮挡。
曲面暂不支持透视或跨对象 BSP 裁切。
