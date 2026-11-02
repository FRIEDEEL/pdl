# 2.1 自己画轮廓和曲线

显式构造几何时，从 `pdl.author.geometry` 导入 `Path`；本例将它别名为 PathGeometry。它是可变的几何构造器。`move_to` 开始子路径，`line_to` 添加线段；`quadratic_to` 使用一个控制点，`cubic_to` 使用两个。`close()` 添加闭合边并把游标返回子路径起点。

将构造器交给 Entity，即可结合样式和移动整个对象。构造器的 `move_to` 添加命令，Entity.move_to 则改变对象位置。坐标采用绝对世界值。新子路径不会自动连接；填充隐式闭合开放子路径，描边仍保持开放。

## 可运行示例与输出

```{literalinclude} ../../../../examples/tutorial/geometry/outline.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![自己连接顶点得到的闭合轮廓](../../../../examples/output/tutorial/geometry/outline.svg)

```{literalinclude} ../../../../examples/tutorial/geometry/curve.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![三次曲线和两条控制辅助线](../../../../examples/output/tutorial/geometry/curve.svg)

完整源码：[outline.py](../../../../examples/tutorial/geometry/outline.py), [curve.py](../../../../examples/tutorial/geometry/curve.py).

---

[本部分目录](index.md)
