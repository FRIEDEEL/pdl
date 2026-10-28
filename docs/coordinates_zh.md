# Author 状态、坐标与数值查询

图形、Text、TeX、Image 和 Group 是唯一的 Author 绘图对象。
几何参数定义局部内容，摆放施加仿射变换，不存在独立 Resolved 模型。

## 立即求值与捕获

`object.anchor(name)` 立即返回当前状态的世界坐标 Point；文字锚点可能触发字体或 TeX 测量。
之后修改对象，不更新这个数值。`move_to`／`place` 当场把变换后边界中心移到指定世界位置；
局部坐标通过显式 frame point 表达。Path.move_to 构建子路径，Path.place 摆放整条路径。
旋转／缩放的默认中心也在操作发生时测量。

使用 `measurement(RendererConfig(...))` 或 `canvas.typography()` 显式选择字体与 TeX 配置。
普通 Text 未指定字体时查找默认字体。构造本身不测量，查询、需要尺寸的摆放和提交会测量。

`Canvas.draw` 使用画布配置捕获状态并固定文字度量。之后修改对象、字体或渲染配置不重新布局
旧记录。`Canvas.snapshot` 不提交绘制，返回作者坐标中的普通捕获 Drawing。
定位计算顺序和 draw 遮挡顺序独立，没有持续锚点依赖。

## 坐标与查询

采用毫米、x 向右、y 向上。CoordinateSystem 表达显式仿射坐标系，点和向量可转换为数值。
`in_space(frame)` 指定局部几何的放置坐标。已有 Entity.space／frame 入口在本轮保留为暂定接口。
局部 Canvas.map 影响后续查询／提交，不改变旧记录；WORLD 映射是最终整页变换。

普通形状 east 是局部锚点变换后的世界位置；Group 使用可见整体的世界轴对齐边界。
偏移使用 `anchor + vector.resolve()`。平移影响点，不影响向量；奇异矩阵不能逆转换。

query 的 point／vector 默认返回最终画布数值，bounds 返回不含描边的几何／排版边界，
ink_bounds 使用字形轮廓。`in_space` 指定作者坐标；from_canvas 逆向转换数值。
查询不绘制对象。fit／auto_size 使用当前提交列表确定视口，因此最终画布查询应在提交后执行。

clip 固定视口，fit 等比例适配固定画布，auto_size 保持比例并确定尺寸。
描边余量为保守估计，文字随几何变换，线宽保持最终画布毫米值。空边界没有锚点。
原生 SVG 与 TeX 字形输出仍可能有差异。

完整规则和示例见 [English guide](coordinates.md)。
