# 3.7 参考系

Frame 是由原点和基向量组成的纯几何。显式创建后，用 point/vector/coordinates 完成数值转换；普通图形使用世界坐标，不自带隐式 frame。

`frame_axes(frame)` 创建显式可绘制 Group，其当前基向量和可视成员一起变换，`.frame` 返回当前纯描述；原始不可变 Frame 保持原样。Gather 可显式选择坐标轴实体和图形，一起移动。

## 可运行示例与输出

```{literalinclude} ../../../../examples/tutorial/geometry/reference_frames.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![左侧参考系固定，右侧参考系显式随图形旋转](../../../../examples/output/tutorial/geometry/reference_frames.svg)

完整源码：[reference_frames.py](../../../../examples/tutorial/geometry/reference_frames.py).

---

[本部分目录](index.md)
