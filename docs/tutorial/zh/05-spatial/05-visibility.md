# 5.5 相交面与可见性

BSP 把相交多边形面拆成前后有序片段，并对支持的凹面环进行三角化。源面对应关系仍可查询，新切割边不会描边。

auto 对无图案的多面体使用 BSP；不支持的内容会警告并回退 centroid。显式 bsp 会拒绝不支持场景。浮点容差、片段预算和树深限制约束算法；此功能用于图示可见性，不提供实体布尔运算或精确算术。

## 可运行示例与输出

```{literalinclude} ../../../../examples/tutorial/spatial/visibility.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![同样的相交板：中心排序与 BSP 可见性](../../../../examples/output/tutorial/spatial/visibility.svg)

![四组中心排序与 BSP 对照](../../../../examples/output/spatial/visibility.svg)

完整源码：[visibility.py](../../../../examples/tutorial/spatial/visibility.py).

---

[本部分目录](index.md)
