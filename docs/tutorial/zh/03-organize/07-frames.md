# 3.7 参考系

## 保持参考系固定，或显式共同变换

`Frame` 保存原点与两个基矢，默认值为 `(0, 0)`、`(1, 0)`、`(0, 1)`，
即与世界轴一致的单位参考系。局部 `(u, v)` 对应
`origin + u * x_basis + v * y_basis`。基矢可以包含缩放与剪切，原点及向量分量以创作毫米计。

每个对象提供独立的 `frame`。赋值只改变参考依据，不改变图形摆放。
变换图形不会改变其参考系；需要共同变换时，显式将两者纳入 `Gather`。

```{literalinclude} ../../../../examples/tutorial/geometry/reference_frames.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![左侧参考系固定，右侧参考系显式随图形旋转](../../../../examples/output/tutorial/geometry/reference_frames.svg)

[完整可运行示例](../../../../examples/tutorial/geometry/reference_frames.py)

两侧均保留灰色原始轮廓与坐标轴。左侧只旋转矩形；右侧 Gather 包含矩形和参考系，
因此共同旋转。`about=box.frame.origin` 指定共同的世界支点，不建立隐含绑定。

## 位置、支点与捕获

- `translate(x, y)` 增加世界坐标位移。
- `rotate(angle, about=...)` 使用逆时针角度；`scale(x, y, about=...)`
  支持非均匀拉伸。支点可以是世界坐标对、已捕获锚点或显式参考系点。
- 省略支点时，普通对象使用变换后局部包围盒的中心，Group 使用可见组边界的中心，
  Frame 使用自身原点。Gather 未指定共同支点时沿用世界原点。
- `frame.point(u, v)` 和 `frame.vector(u, v)` 表达位置与位移。
  `move_to(frame.point(...))` 当场计算并固定目标位置，不持续跟随参考系。
- `anchor(...)` 当场测量并返回固定数值点，后续修改不改变该锚点。
- `draw()` 捕获状态并固定文字度量，之后修改不改变已提交记录。

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

API：{py:class}`pdl.Entity`、{py:class}`pdl.Frame`、
{py:class}`pdl.ReferencePoint`、{py:class}`pdl.Gather`。

---


查询边界，以及必须保持依赖文字测量的世界姿态的重新成组操作，若无法延后测量，
需要在有效字体上下文中执行。

---

[本篇目录](index.md)
