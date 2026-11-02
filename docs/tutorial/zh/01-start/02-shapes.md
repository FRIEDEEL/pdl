# 1.2 画几个基本图形

圆、矩形、线段、折线、多边形和弧均可通过绘图工厂创建，参数采用当前世界坐标，单位毫米。`Circle(...)` 返回 Entity；`pdl.author.geometry.Circle(...)` 创建纯几何，可再用 `Entity(geometry, style=...)` 组合。

Point 和裸 Geometry 提供数值描述，Canvas 接收 Entity 或可展开组件。弧的端点／角度构造器属于纯 `Arc` 几何类型，绘制前需要包装成 Entity。

## 可运行示例与输出

```{literalinclude} ../../../../examples/tutorial/basics/shapes.py
:language: python
:start-at: from pdl import
:end-before: output =
```

![shapes](../../../../examples/output/tutorial/basics/shapes.svg)

```{literalinclude} ../../../../examples/tutorial/basics/coordinates.py
:language: python
:start-at: from pdl import
:end-before: output =
```

![coordinates](../../../../examples/output/tutorial/basics/coordinates.svg)

完整源码：[shapes.py](../../../../examples/tutorial/basics/shapes.py), [coordinates.py](../../../../examples/tutorial/basics/coordinates.py).

---

[本部分目录](index.md)
