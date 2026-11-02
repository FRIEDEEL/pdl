# 5.7 投影图层：材料与 probe

需要显式安排图示覆盖时，可以分别投影组件。共享相机和世界坐标可对齐数值位置，独立投影之间的覆盖由之后的 Canvas 顺序决定。

把投影结果与文字、引线放入 Group，即可立即进行 2D 编辑。独立投影不共享深度缓冲或跨场景拆面，源查询跟随投影 Group 当前的 2D 坐标。

## 可运行示例与输出

```{literalinclude} ../../../../examples/tutorial/spatial/projected_layers.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![材料参考与独立投影的 probe、二维标注并排展示](../../../../examples/output/tutorial/spatial/projected_layers.svg)

完整源码：[projected_layers.py](../../../../examples/tutorial/spatial/projected_layers.py).

---

[本部分目录](index.md)
