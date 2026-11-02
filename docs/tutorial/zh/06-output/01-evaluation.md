# 6.1 从对象到图像

位置查询对当前依赖求值并返回固定 Point；只有需要尺寸或轮廓的操作才调用字体／TeX 工具。Transform 立即保存变换结果，以及需要明确改变的样式值。

Canvas.snapshot 捕获普通 Entity，不提交绘制；Canvas.add/draw 还记录覆盖顺序，并固定有效样式和排版。之后的对象修改、全局默认值或字体策略不会重排已有记录。后端编码捕获的 Entity，不存在第二套 resolved 场景模型。

## 可运行示例与输出

```{literalinclude} ../../../../examples/tutorial/advanced/snapshots.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![原标签与移动后的标签](../../../../examples/output/tutorial/advanced/snapshots.svg)

![固定的原标签](../../../../examples/output/tutorial/advanced/snapshots-copy.svg)

完整源码：[snapshots.py](../../../../examples/tutorial/advanced/snapshots.py).

---

[本部分目录](index.md)
