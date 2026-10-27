# Authoring 状态、坐标空间与求值

本文对应英文文档 [coordinates.md](coordinates.md)。

## 职责与状态捕获

数值几何类型 Rectangle、Circle、Polygon 和 Path 描述局部形状；Entity
提供可原地修改的放置句柄；Drawing 是放置记录；Group 表达有序复用组件。
继续支持直接绘制既有数值几何，不要求迁移所有旧代码。

Entity 的 move_to 将变换后局部边界中心移到目标位置。transform、translate、
rotate、scale、reflect 修改句柄并返回自身。后加变换作用在已有放置之外；
旋转默认绕 Authoring 世界原点，可指定 center。一起移动的内容用 Group 组合。

Entity.anchor()、Entity.space 捕获调用时描述状态，不立即测量。目标随后修改
不影响既有捕获；Canvas.draw() 同样捕获内置可变描述，包括共享 Path。
自定义 Composite 必须提供不可变描述，不自动冻结任意用户可变对象。

捕获描述仍使用本次 Canvas 字体求值；显式 canvas.resolve() 才固定测量结果。

## 坐标空间

默认世界坐标以毫米为单位、左下原点、x 向右、y 向上。子空间可嵌套；
canvas.map(frame, matrix) 覆盖该空间相对父空间的映射，map(WORLD, matrix)
配置世界到画布的基础映射。不同 Canvas 可采用不同配置。

Entity.move_to 的普通坐标属于父空间；带空间点和锚点引用会自动转换。
Entity.space 的原点沿用数值几何原点，不自动改为边界中心。

形状局部 east 锚点随变换移动；它不等于世界包围盒 east。显式使用
anchor.shifted(space.vector(x, y)) 区分局部／世界偏移。平移影响点，不影响向量。
逆向转换遇到奇异矩阵报错，正向变换允许退化。

## 查询与输出

依赖顺序决定先测量谁；draw 顺序决定遮挡。求值不自动加入绘制对象。
常规绘图无需调用 query 或 resolve。

- query().point 返回数值点，bounds 返回不含描边的几何／排版边界。
- ink_bounds 使用字形实际轮廓；in_space 指定适配前的 Authoring 空间。
- from_canvas 将数值 Canvas 点转换为固定 Authoring 坐标，不恢复依赖。
- resolve 返回 Canvas 坐标中的确定快照，保留基础形状、变换、已测量文字和 Node。
- 后端优先原生表达，不支持时拆解。快照在另一 Canvas 绘制时仍受目标画布适配影响。

fit／auto_size 查询使用当前绘制列表确定视口；没有绘制内容时，bounds／resolve
使用被查询对象适配。空绘制列表的点／向量查询只使用基础映射。

## 画布策略与边界

clip 默认固定视口裁剪；fit 固定画布、等比例缩放居中；auto_size 保持比例，
按内容确定尺寸。后两者支持 padding。文字随几何缩放，线宽保持画布毫米值。
适配使用排版边界和保守描边余量，不宣称精确外观边界。

空几何不会把原点加入整体边界，is_empty 为真且没有锚点。内置坐标不包含依赖
画布宽高的比例单位，因此不会引入画布尺寸循环。非线性坐标、精确描边边界、
自动布局／寻路、曲线长度、最近点和一般求交后置。

示例 examples/coordinates/relationships.py 演示状态捕获、变换后重新挂接、
镜像／旋转组合、文字依赖和三种画布策略。
