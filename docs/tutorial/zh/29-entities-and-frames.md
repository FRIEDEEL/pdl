# 29. 可编辑对象与显式参考系

`Circle`、`Line`、`Path`、`Text`、`TeX`、`Node`、`Connection`、`Image`、
`ProjectedScene` 和 `Group` 共享 `Entity` 基类。直接操作具体对象即可，
无需额外写 `Entity(shape)`。几何参数描述局部内容，变换修改摆放并返回自身；
需要独立保留一个可编辑版本时，使用 `copy()`。

## 保持参考系固定，或显式共同变换

`Frame` 保存原点与两个基矢，默认值为 `(0, 0)`、`(1, 0)`、`(0, 1)`，
即与世界轴一致的单位参考系。局部 `(u, v)` 对应
`origin + u * x_basis + v * y_basis`。基矢可以包含缩放与剪切，原点及向量分量以创作毫米计。

每个对象提供独立的 `frame`。赋值只改变参考依据，不改变图形摆放。
变换图形不会改变其参考系；需要共同变换时，显式将两者纳入 `Gather`。

```{literalinclude} ../../../examples/tutorial/geometry/reference_frames.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![左侧参考系固定，右侧参考系显式随图形旋转](../../../examples/output/tutorial/geometry/reference_frames.svg)

[完整可运行示例](../../../examples/tutorial/geometry/reference_frames.py)

两侧均保留灰色原始轮廓与坐标轴。左侧只旋转矩形；右侧 Gather 包含矩形和参考系，
因此共同旋转。`about=box.frame.origin` 指定共同的世界支点，不建立隐含绑定。

## 位置、支点与捕获

- `translate(x, y)` 增加世界坐标位移。
- `rotate(angle, about=...)` 使用逆时针角度；`scale(x, y, about=...)`
  支持非均匀拉伸。支点可以是世界坐标对、已捕获锚点或显式参考系点。
- 省略支点时，普通对象使用变换后局部包围盒的中心，Group 使用可见组边界的中心，
  Frame 使用自身原点。Gather 未指定共同支点时沿用世界原点。
- `frame.point(u, v)` 和 `frame.vector(u, v)` 表达位置与位移。
  `move_to(frame.point(...))` 显式建立定位依赖，在捕获或后续摆放操作前跟随参考系。
- `anchor(...)` 保留现有快照语义：描述调用时的状态，测量可以延后，后续修改不改变该锚点。
- `draw()` 捕获状态与引用，之后修改不改变已提交记录；文字测量和布局求值仍可延后到渲染。

`center=` 保留为 `about=` 的兼容别名，二者不可同时传入。
`Path.move_to` 仍用于构建路径；摆放整条路径请使用 `place(...)`。
其他对象支持 `move_to` 和 `place`。几何与字形一起接受仿射变换，线宽保持画布毫米值；
非均匀缩放也会拉伸字形。

## 不绘制的参考对象

`Frame` 和 `ReferencePoint` 是 Entity，可以加入 Group 或 Gather。
它们不产生绘制内容，不计入可见包围盒、自动适配范围，也不产生遮挡几何，
不会进入三维 BSP 计算。直接 `draw(frame)` 不产生可见内容；已成组的成员仍应通过最外层组提交。

`frame.visualize(...)` 返回独立可绘制的 Group。轴长、原点标记半径和轴／标记样式由参数控制，
不存入 Frame。`axis_length` 使用局部单位，因此基矢长度影响显示。
可视化结果捕获调用时的参考系，后续修改不会使它跟随；生成的内容参与普通边界和绘制顺序。

## 迁移旧代码

将 `Entity(Circle(...), style=paint)` 改为 `Circle(...).set_style(paint)`。
旧 `Entity(geometry, space=...)` 保留为兼容入口，以继续支持 `CoordinateSystem` 与 Canvas 映射。
兼容包装省略旋转／缩放支点时保留原来的世界原点默认值；直接操作具体对象则默认使用自身中心。
迁移需要围绕世界原点的操作时，显式写 `about=(0, 0)`。
现有 Drawing 描述与不可变 CoordinateSystem 身份仍受支持，与新的可编辑 Frame 分开。
`Group.transformed(...)` 仍返回捕获描述；需要另一个可编辑组时，使用
`group.copy().apply_transform(...)`。

Group 仍独占管理成员，Gather 仍为扁平操作集合。普通 Entity 不提供通用父子关系 API。

API：{py:class}`pdl.Entity`、{py:class}`pdl.Frame`、
{py:class}`pdl.ReferencePoint`、{py:class}`pdl.Gather`。

---

[上一章：投影图层](28-projected-layers.md)

查询边界，以及必须保持依赖文字测量的世界姿态的重新成组操作，若无法延后测量，
需要在有效字体上下文中执行。
