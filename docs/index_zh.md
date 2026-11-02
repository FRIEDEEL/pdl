# 用 pdl 绘图

| 构建信息 | 内容 |
| --- | --- |
| 版本 | {{ build_version }} |
| Commit | {{ build_commit }} |
| 分支 | {{ build_branch }} |

pdl 是用于静态矢量绘图的 Python 库。从一个带标签的小方框开始，学习形状和样式，
再构建相互连接、可以复用的组件。同一套绘图对象可以输出 SVG 或 TikZ。
绘图工厂返回包含当前几何和可选 Style 的 Entity。编辑立即生效，Canvas 捕获独立的提交结果。

## 开始绘图

- [中文教程](tutorial/zh/index.md)
- [API 参考（英文）](api_zh.md)：查询精确签名、默认值、单位和行为。

```{toctree}
:maxdepth: 3
:caption: 教程

tutorial/zh/index
```

```{toctree}
:maxdepth: 2
:caption: 参考与指南

api_zh
architecture_zh
coordinates_zh
flowcharts_zh
spatial_zh
tikz-output_zh
```

## 能力范围

当前支持形状、路径、普通文字、TeX、节点、连接、组合、仿射变换、显式参考系和视口适配。
也支持可编辑 Group、允许重叠的 Gather、有序 Layer、PNG/JPEG 图片、逐叶对象透明度，
以及线性和径向渐变填充。尚未实现图层组合、隔离合成、通用自动图布局和自动路由。
生长式流程图支持按边界间距进行方向定位和编辑连接。公开接口仍处于开发阶段。

[构建与维护文档](building_zh.md)。

教学参考：[Manim Community Quickstart](https://docs.manim.community/en/stable/tutorials/quickstart.html)
和 [PGF/TikZ manual](https://tikz.dev/)。它们的 API 与 pdl 不同；
这里只支持文档中明确说明的 pdl 接口。

```{toctree}
:hidden:

building_zh
```
