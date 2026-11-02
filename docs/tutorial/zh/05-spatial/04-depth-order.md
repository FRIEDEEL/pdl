# 5.4 透明度与深度顺序

一次投影内部决定覆盖顺序。sort_faces=False 保留输入对象／面顺序，centroid 按中心深度近似排序。重排 ProjectedScene 会复制成员，并保留源位置对应关系。

透明度按面设置，背面仍会保留。整面中心排序可能无法处理相交或环状遮挡；满足多边形场景条件时使用 BSP。

## 可运行示例与输出

```{literalinclude} ../../../../examples/tutorial/spatial/depth_order.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![透明面与自动／手动顺序对照](../../../../examples/output/tutorial/spatial/depth_order.svg)

完整源码：[depth_order.py](../../../../examples/tutorial/spatial/depth_order.py).

---

[本部分目录](index.md)
