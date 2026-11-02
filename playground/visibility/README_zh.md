# 平面遮挡实验

本目录是独立原型，**不修改 pdl 公共 API**。当前支持不透明、凸、共面的多边形，
采用 BSP 按支撑平面切分，按相机位置从远到近遍历，最终返回普通二维
`ProjectedScene`。相交面、循环遮挡都可通过切分处理；不以面中心深度决定顺序。

## 运行与输出

在仓库根目录执行：

```sh
uv run python -m playground.visibility.run --counts 32 96 256 --repeats 3 --samples 1024
uv run python -m pytest playground/visibility/test_bsp.py -q
uv run pyright playground/visibility
```

缓存受限时，在命令前加 `UV_CACHE_DIR=/private/tmp/pdl-uv-cache`。
生成文件位于忽略目录 `output/`：

- `comparison.svg/.tex/.pdf`：同一透视相机和配色下，对比现有中心排序与 BSP。
  包括平行面反例、相交面、三个互不相交条带形成的循环遮挡、随机稠密场景。
- `sparse-*.svg`、`medium-*.svg`、`dense-*.svg`：每个性能场景的实际矢量输出。
- `timings.csv`、`results.json`：耗时中位数／最小／最大值、输入面数、片段数、
  切分次数、树深、随机种子及平台／相机信息。

PDF 对照图需要 XeLaTeX；没有增加 Python 依赖。可用 Ghostscript 等工具转 PNG。

## 计时和验证

随机生成、后续 Canvas 求值、字体测量、导出、PDF 编译、射线验证均不计入计时。
计时包括近面检查、源面查询元数据、BSP 构建、遍历、投影与二维 Authoring 构造。
每次重建 BSP，不复用缓存；报告总时间多次运行的中位数和范围，分阶段时间取最后一次。
基线计时为当前公开的 `Scene3D.project()`，源对象构造同样放在计时之外。

位置采样于固定 100 mm 立方体，法向均匀分布于球面，形状为随机长宽比／旋转的
3–7 边凸多边形。稀疏至稠密保持相同随机参数，仅增加面尺寸。
独立射线验证将原始面的最近交点，与二维片段最后覆盖的源 ID 对比。
一半射线均匀覆盖画面，另一半瞄准源面内部，避免稀疏场景只测到背景。
这是抽样验证，不是逐像素正确性的证明。

测试另检查面积与原边总长度守恒、过顶点切分、共面优先级及异常路径；
循环案例还检查完整面的所有排列都无法正确显示。

## 边界

每个片段保留源 ID，只对原边描线，切分边不产生新轮廓。共面重叠按较大源 ID
在上处理；二维源点查询数组仍按输入顺序索引。BSP 的无限支撑平面可能切开实际上
互不相交的有限面，因此会产生额外片段。

仅支持符合前提的凸平面面片，不全面验证任意用户多边形；不支持凹面、孔、曲面、
透明度、面内图案、阴影或实体布尔。跨近面直接报错，不静默裁切。
采用浮点及绝对 `1e-8` mm 容差，并非精确算术；容差范围内可能视为共面。
达到 100,000 片段或树深 500 的安全预算时报错，不退回中心排序。
尚未加入投影范围筛选、空间索引或数值内核优化。矢量查看器的抗锯齿可能显示细缝，
它不同于新增描边；没有像素基准测试。

实测数据及解释见 [RESULTS.md](RESULTS.md)，详细设计见 [英文说明](README.md)。

## 正式库实现

pdl 现已将 BSP 接入 `Scene3D.project()`，支持凹面分解、源面对应及明确的算法选择；
本目录原型保留为历史实验。运行 `uv run python -m playground.visibility.library`，
可对正式公开接口计时，并将实际返回的二维绘制片段与独立射线求交结果比较。
输出 `output/library-*.svg`、`library-results.json`、`library-timings.csv`。
原性能脚本基线已显式选择 centroid，防止库升级后参照算法改变。
参见[正式教程](../../docs/tutorial/zh/05-spatial/05-visibility.md)。


## API 迁移

保留 BSP 算法和历史结果；输出构造已改用当前 Entity／Group 工厂及 extensions.spacial 路径。历史计时仍描述原始运行，比较当前性能前应重新运行基准。
