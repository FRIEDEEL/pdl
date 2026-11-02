# 3.4 控制图层上下顺序

Layer 属于 Canvas，负责覆盖顺序。整数层在提交时绑定到 Canvas 的图层身份；插入或重排图层会一起移动已有记录。显式 Layer 身份只属于一个 Canvas。

Group 在成员最高层连续绘制，并保持原各层内的顺序。对成员设置层会警告并提升到最外层 Group。Gather 可跨层选择对象，不会合并覆盖顺序。

## 可运行示例与输出

```{literalinclude} ../../../../examples/tutorial/layout/layers.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![18. 控制图层上下顺序](../../../../examples/output/tutorial/layout/layers.svg)

![Layer、Gather 与 Group 的三种结果](../../../../examples/output/composition/sandwich.svg)

完整源码：[layers.py](../../../../examples/tutorial/layout/layers.py).

---

[本部分目录](index.md)
