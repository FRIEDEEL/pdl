# 2.3 复制与捕获

Entity.copy 创建独立几何及 Group 成员，并解除根对象的父级和图层身份，用于保留可继续编辑的版本。Canvas 提交会再捕获独立状态，之后移动原对象不会改变已经记录的图形。

Entity 初始化时直接持有传入几何。显式共享可变 Path 时，直接修改构造器会影响共享者；Transform 仅替换目标实体持有的几何。需要批量操作时使用 Gather。

## 可运行示例与输出

```{literalinclude} ../../../../examples/tutorial/geometry/copy_and_capture.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![灰色旧记录、蓝色移动结果与独立橙色副本](../../../../examples/output/tutorial/geometry/copy_and_capture.svg)

完整源码：[copy_and_capture.py](../../../../examples/tutorial/geometry/copy_and_capture.py).

---

[本部分目录](index.md)
