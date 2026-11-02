# 3.6 不绘制的参考点

Point 是不可变的数值参照。Entity 的参考点用于默认旋转／缩放；set_reference 改变支点，不移动几何。`move_to(position)` 对齐参考点，`anchor=` 则指定逻辑包围盒锚点。

参照点与可视标记分别创建；需要显示点时，提交一个 Circle Entity。位置查询返回当次数值，后续修改不会建立持续附着关系。

## 可运行示例与输出

```{literalinclude} ../../../../examples/tutorial/layout/reference_points.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![矩形围绕标出的参考点旋转](../../../../examples/output/tutorial/layout/reference_points.svg)

完整源码：[reference_points.py](../../../../examples/tutorial/layout/reference_points.py).

---

[本部分目录](index.md)
