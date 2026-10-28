# 2.3 复制与捕获

变换修改自身并返回自身。需要另一个可编辑对象时使用 `copy()`，之后两者独立修改。
复制 Group 时包含独立成员。

```{literalinclude} ../../../../examples/tutorial/geometry/copy_and_capture.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![灰色旧记录、蓝色移动结果与独立橙色副本](../../../../examples/output/tutorial/geometry/copy_and_capture.svg)

[完整源码](../../../../examples/tutorial/geometry/copy_and_capture.py)

灰圆是原始位置的绘制记录；蓝圆是原对象移动后的结果；橙圆是独立副本，位置不受原对象修改影响。

| 操作 | 得到什么 |
| --- | --- |
| `object.copy()` | 独立、可编辑的对象 |
| `object.anchor(...)` | 调用时的锚点描述，测量可延后 |
| `canvas.draw(object)` | 固定描述的绘制记录，之后编辑对象不改变它 |
| `canvas.resolve(object)` | 使用画布配置确定位置与文字度量的结果 |

引用与 draw 捕获的是描述，不一定已得到字体相关数值。求值篇再详细解释 resolve。
后面介绍的 `frame.visualize()` 也会生成独立的可绘制快照。

[本篇目录](index.md)
