# 源码架构

## 当前重构边界

旧实现和测试已移至 `src/pdl_old` 与 `tests_old`，新 `src/pdl` 按依赖关系逐步重建。
当前确定的 Author 分工如下：

| 包 | 职责 | 允许依赖 |
| --- | --- | --- |
| `author.geometry` | 各类独立几何描述及自身的数学查询 | 标准库、transform，必要时使用 util |
| `author.style` | 样式描述 | 标准库，必要时使用 util |
| `author.entity` | 绘图实例、对象关系及用户操作 | geometry、style、transform、util |
| `author.transform` | 广义空间变换契约及具体仿射矩阵 | 标准库和 util，不依赖其他 pdl 领域包 |
| `author.util` | 纯数值函数及字体／TeX 等外部工具接口 | 标准库、第三方库与外部工具；不依赖其他 pdl 层 |

首批实现为 `point.py` 与 `path.py`。Point 是不可变的有限坐标值；Path 是可变构造器，
提供不可变的路径命令快照。二者不继承共同 Geometry 基类，不依赖 Entity、Style、
绘图后端或旧包。普通坐标默认相对 Author 世界，不附带隐式局部参考系。
几何描述是否可变由具体类型定义，不通过共同基类统一规定。

此阶段通过具体模块导入：

```python
from pdl.author.geometry.point import Point
from pdl.author.geometry.path import Path
```

`author.transform` 与 geometry、entity 平级。Transform 只约定数值坐标对的映射，
不要求所有变换具有矩阵、逆变换或对象类型分派。AffineTransform 保存有限的仿射矩阵；
用户可通过 Translation、Rotation、Scaling、Shear、Reflection 子类创建变换。
这些仿射类型的矩阵值不可变。`left @ right` 先应用 right，返回一般 AffineTransform；
仿射类提供求逆，奇异矩阵明确报错。`around((x, y))` 接收显式支点，不读取对象参考点。

```python
from pdl.author.transform.affine import Rotation, Translation

mapping = Translation(10, 0) @ Rotation(90)
coordinates = mapping.apply((1, 0))  # Approximately (10, 1).
```

变换包不导入 Point、Path、Entity 或 Style。Geometry／Entity 自行将数据适配为数值坐标对，
并定义所支持的应用行为。路径变换、参考点查询、边界、字体排版、Entity、Canvas 和后端尚未重建。
非线性／网格变换及其组合、路径近似策略留待后续讨论。

`author.style.color.Color` 是通道范围为 [0, 1] 的不可变 RGB 值。
`author.style.style.Style` 描述纯色填充／描边、毫米线宽、端点／连接样式、填充规则和透明度。
它是完整的不可变值，不包含几何、对象归属、输出编码或默认值／继承解析。
Style 内部的 None 表示关闭对应填充或描边，与未来 Entity 的 `style=None` 使用 Group 或类型默认值不同。
Style 构造器默认黑色 1 mm 描边、无填充，不强制所有 Entity 类型采用这些默认值。
本步不实现渐变、字体属性、类型默认值和 Group 合成语义。

```python
from pdl.author.style.color import Color
from pdl.author.style.style import Style

paint = Style(stroke=None, fill=Color(0.2, 0.4, 0.8), opacity=0.75)
```

当前测试在 `tests/unit/author/` 下镜像 geometry、transform、style；不通过导入 `pdl_old` 补齐功能。
设计结论及未定问题见临时的 `refactor_note.md`。

## 旧架构（仅供参考）

下文描述重构前、现位于 `src/pdl_old` 的实现，不代表新 `pdl` 已实现的接口或定位契约。

Author 是唯一绘图对象模型。测量是一种操作，不是第二套场景表示。
锚点立即返回当前状态的数值点，后续修改不改变旧结果。字体和 TeX 测量可以在
Author 阶段执行，与最后输出和遮挡顺序无关。

## 模块分工

| 包 | 职责 | 允许依赖 |
| --- | --- | --- |
| `foundation.geometry` | 数值点、向量、路径、矩阵、边界算法 | 标准库 |
| `foundation.typography` | 字体、塑形、TeX 测量、轮廓及测量配置 | foundation、外部字体／TeX 工具 |
| `author` | 可编辑二维图形、文字、公式、图片、组合、参考、样式和图层身份 | foundation、author |
| `canvas` | 提交捕获、图层排序、查询、视口和导出入口 | author、foundation、backend 入口 |
| `backends` | SVG／TikZ 编码、原生图元选择、降级和 PDF 编译 | author、foundation、`canvas.records.Page` |
| `extensions.diagrams` | 节点、连接和生长流程图 | author、foundation、extensions |
| `extensions.spatial` | 三维几何、相机、投影和可见性 | author、foundation、extensions |

依赖方向与详细英文文件清单见 [English architecture](architecture.md)。
Canvas 调用 backend；backend 只读取尺寸与绘制记录组成的 Page 协议，不导入 Canvas 实现。
Author 声明图层身份，Canvas 实现 LayerStack 排序，两者通过小协议连接。

根 `pdl` 是延迟导入的公共门面。导入 Canvas、Circle 不加载 3D 或图表扩展；
`pdl.author` 可以作为独立二维入口。

## 求值与输出

1. 创建与编辑 Author 对象。查询锚点、按中心定位和使用默认旋转支点时可以立即测量文字。
2. 数值结果固定。通过 `measurement(RendererConfig(...))` 或 `canvas.typography()`
   指定测量配置；未指定的普通文字查找默认字体。
3. `draw()` 使用画布配置捕获几何、变换和文字度量，将高级组件展开成核心二维描述。
4. 最终提交列表决定 fit／auto-size；backend 编码输出，不重新计算锚点关系或访问高级组件。

`Canvas.snapshot()` 返回作者坐标中的普通 Drawing，不提交绘制。
移除 `Canvas.resolve`、`ResolvedGraphic`、公开延迟 AnchorRef 和测量专用文字子类。
TikZ 不再重新布局原生图表节点，而是输出固定图形和独立定位的文字。
原生字体输出仍可能与测量存在差异，不承诺 SVG 与 TeX 逐像素相同。

本轮保留了 Author 内已有的显式坐标系和 Entity frame／space 访问入口，仍属暂定 API；
后续简化可以独立进行。Canvas 的局部坐标映射影响后续查询与提交，不修改旧捕获记录；
WORLD 映射和 fit 属于最终页面变换。

## 边界检查

`tests/architecture/test_boundaries.py` 检查模块依赖，包括函数内和仅类型使用的导入，
并以独立进程验证基础设施与二维核心不加载上层扩展。
行为测试覆盖立即求值、独立遮挡顺序、捕获隔离、复制与分组、文字、图表和三维投影。
