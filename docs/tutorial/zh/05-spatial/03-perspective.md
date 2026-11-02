# 5.3 透视投影

PerspectiveCamera 按 distance、focal_length、near 参数进行针孔投影。位于或越过 near 边界的几何会报错，不会自动裁剪。

透视平面的曲线和字形会细分为矢量路径，后续 2D 缩放前的投影控制包络容差为 0.02 毫米。曲面形体和图片使用已说明的正交／原生流程；独立 2D 图例仍是普通文字。

## 可运行示例与输出

```{literalinclude} ../../../../examples/tutorial/spatial/perspective.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![平面图案与 D10 的正交和透视对比](../../../../examples/output/tutorial/spatial/perspective.svg)

完整源码：[perspective.py](../../../../examples/tutorial/spatial/perspective.py).

---

[本部分目录](index.md)
