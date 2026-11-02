# 2.2 移动、旋转和缩放

变换立即生效。平移改写位置，旋转和缩放默认围绕实体参考点，也可通过 `origin=` 指定支点。矩形默认参考左下角，圆参考圆心，Path 参考第一次移动的位置，文字／TeX 参考基线。

几何转换由 transform 包决定。拉伸后的圆成为 Path，Entity 身份保持不变。默认线宽固定；均匀 `Rescale(factor, include_linewidth=True)` 或 `entity.rescale(..., include_linewidth=True)` 可同步缩放线宽，非均匀 Scaling 不提供这个选项。

## 可运行示例与输出

```{literalinclude} ../../../../examples/tutorial/geometry/translation.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![原位置的灰色轮廓和移动后的矩形](../../../../examples/output/tutorial/geometry/translation.svg)

```{literalinclude} ../../../../examples/tutorial/geometry/rotation.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![绕红色中心点旋转后的矩形](../../../../examples/output/tutorial/geometry/rotation.svg)

```{literalinclude} ../../../../examples/tutorial/geometry/scaling.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![圆经过不等比例缩放形成椭圆](../../../../examples/output/tutorial/geometry/scaling.svg)

完整源码：[translation.py](../../../../examples/tutorial/geometry/translation.py), [rotation.py](../../../../examples/tutorial/geometry/rotation.py), [scaling.py](../../../../examples/tutorial/geometry/scaling.py).

---

[本部分目录](index.md)
