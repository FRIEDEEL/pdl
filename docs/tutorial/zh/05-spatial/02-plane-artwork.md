# 5.2 把图案放进平面

Plane3D 为 2D 图案提供显式原点和两个 3D 基向量，投影确定实际 2D 几何。普通 Text 在保持朝向手性的相似变换下保留原生形式；TeX 平移／旋转保留源码，缩放及其他仿射平面变形则生成已测量的轮廓。

图案在排序前与表面组合，不会自动裁剪或受光照。带图案的场景显式选择 centroid 排序，并把图案放在目标面边界内。

## 可运行示例与输出

```{literalinclude} ../../../../examples/tutorial/spatial/plane_text.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![平放与倾斜平面上的原生文字](../../../../examples/output/tutorial/spatial/plane_text.svg)

完整源码：[plane_text.py](../../../../examples/tutorial/spatial/plane_text.py).

---

[本部分目录](index.md)
