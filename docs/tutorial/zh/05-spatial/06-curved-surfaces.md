# 5.6 圆柱曲面

Sphere、Cylinder、CylinderSurface、AnnularCylinder 提供平滑的正交图示形体，光照可产生连续渐变填充，表面弧通过当前 2D 路径几何表达。

曲面场景使用 centroid／manual 排序，不参与多边形 BSP。表面变换遵循其相似变换限制。可比较极限视角，以及组装结果旁保留的原始参照。

## 可运行示例与输出

```{literalinclude} ../../../../examples/tutorial/spatial/cylinder_surface.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![从内部观察开放的半圆柱面](../../../../examples/output/tutorial/spatial/cylinder_surface.svg)

```{literalinclude} ../../../../examples/tutorial/spatial/washer.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![中央孔洞保持开放的垫圈](../../../../examples/output/tutorial/spatial/washer.svg)

![垫圈和开放曲面的俯视、仰视、侧视与沿轴视图](../../../../examples/output/spatial/material_probe-views.svg)

完整源码：[cylinder_surface.py](../../../../examples/tutorial/spatial/cylinder_surface.py), [washer.py](../../../../examples/tutorial/spatial/washer.py).

---

[本部分目录](index.md)
