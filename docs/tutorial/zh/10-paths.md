# 10. 自己画轮廓和曲线

内置图形不够用时，可以用 {py:class}`pdl.Path`。
它记录一串操作：把笔移到某处、画线、画曲线，或者闭合轮廓。
Path 本身没有颜色，绘制时再指定样式。

## 连接几个点

```{literalinclude} ../../../examples/tutorial/geometry/outline.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![自己连接顶点得到的闭合轮廓](../../../examples/output/tutorial/geometry/outline.svg)

[完整可运行示例](../../../examples/tutorial/geometry/outline.py)

move_to 只选择起点，不画连接线。每次 line_to 增加一条直线。
close() 补上回到起点的最后一条边。这些方法修改原 Path，并返回它，所以可以连续调用。

所有位置都是绝对的局部坐标。再次 move_to 可以另起一段，不会与前一段相连。
没有 close 的子路径也可以填充，填充时视作闭合，但描边不会因此自动补上闭合边。

## 画一条弯曲的线

```{literalinclude} ../../../examples/tutorial/geometry/curve.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![三次曲线和两条控制辅助线](../../../examples/output/tutorial/geometry/curve.svg)

[完整可运行示例](../../../examples/tutorial/geometry/curve.py)

曲线从 `(10, 10)` 出发，在 `(45, 10)` 结束。
两个控制点是 `(10, 35)` 和 `(45, 35)`，图中用小圆标出。
灰色辅助线表示控制手柄：曲线从起点朝第一个控制点的方向出发，
再沿第二个控制点指向终点的方向抵达终点，通常不会经过控制点本身。

`quadratic_to(control, end)` 是只用一个控制点的版本。
画直线或贝塞尔曲线前，需要先 move_to。
`Path.arc(Arc(...))` 可以接入圆弧，必要时先连到圆弧起点，并用三次曲线近似。

## 自己试试

把第一个控制点从 `(10, 35)` 降到 `(10, 20)`，同时修改它的辅助线和标记。
曲线的左侧会变平。

执行 `canvas.draw(path)` 后，再编辑 Path 不会改变已经记录的那次绘制。
要记录新状态，需要再次 draw。[多子路径与填充规则](15-fill-rules.md)放在渲染章节之后。

接口说明：{py:class}`pdl.Path`、{py:class}`pdl.Arc`。

---

[上一章：组合与复用](09-groups.md) · [下一章：几何查询](11-geometry-queries.md)
