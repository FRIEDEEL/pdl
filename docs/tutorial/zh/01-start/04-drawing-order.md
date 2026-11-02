# 1.4 谁挡住谁？

Canvas 在提交时捕获对象的当前状态。同一 Layer 中后提交的内容覆盖先提交的内容；调整绘制顺序不会改变此前计算的锚点与位置。

被引用位置的对象仍需显式提交才会显示。后续修改后再次 `add` 或 `draw`，会记录另一份独立状态。

## 可运行示例与输出

```{literalinclude} ../../../../examples/tutorial/layout/circle_first.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![矩形后画，遮住圆的一部分](../../../../examples/output/tutorial/layout/circle_first.svg)

```{literalinclude} ../../../../examples/tutorial/layout/rectangle_first.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![圆后画，遮住矩形的一部分](../../../../examples/output/tutorial/layout/rectangle_first.svg)

完整源码：[circle_first.py](../../../../examples/tutorial/layout/circle_first.py), [rectangle_first.py](../../../../examples/tutorial/layout/rectangle_first.py).

---

[本部分目录](index.md)
