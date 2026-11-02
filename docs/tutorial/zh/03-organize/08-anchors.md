# 3.8 挂接物件与连接节点

Entity.anchor 根据当前几何／排版的逻辑包围盒返回 Point，不包含描边。方向名称对应世界轴对齐矩形；Node 的圆形对角端口位于圆周。

创建其他对象或 Connection 时查询源位置。得到的数值和连接端点不会随着源对象后续修改而变化；需要新位置时，重新查询并构建依赖对象。

## 可运行示例与输出

```{literalinclude} ../../../../examples/tutorial/layout/anchors.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![通过边缘锚点连接的两个节点](../../../../examples/output/tutorial/layout/anchors.svg)

```{literalinclude} ../../../../examples/tutorial/layout/captured_anchors.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![旧挂接留在下方，新挂接使用移动后的矩形](../../../../examples/output/tutorial/layout/captured_anchors.svg)

完整源码：[anchors.py](../../../../examples/tutorial/layout/anchors.py), [captured_anchors.py](../../../../examples/tutorial/layout/captured_anchors.py).

---

[本部分目录](index.md)
