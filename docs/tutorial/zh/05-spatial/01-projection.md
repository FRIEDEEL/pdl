# 5.1 先投影三维，再绘制二维

3D 对象从 `pdl.extensions.spatial` 显式导入，根入口不再直接提供这些名称。

构造右手系 3D 坐标和形体，选择相机，再显式调用 Scene3D.project。结果是普通 2D ProjectedScene Group，可与核心 Entity 组合并交给两个后端。

源顶点与面中心的索引查询不依赖绘制顺序。后续 2D 编辑一起更新这些数值查询和可视成员，源 3D 场景保持原样。

## 可运行示例与输出

```{literalinclude} ../../../../examples/tutorial/spatial/projection.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![投影立方体与二维标注](../../../../examples/output/tutorial/spatial/projection.svg)

完整源码：[projection.py](../../../../examples/tutorial/spatial/projection.py).

---

[本部分目录](index.md)
