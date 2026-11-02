# 6.3 在局部坐标系里画图

构造图形前可使用显式 Frame 转换，Frame.point 返回固定世界位置。`canvas.map(WORLD, affine)` 选择最终世界到页面的映射，不改写源 Entity。

Canvas 的查询坐标系覆盖作用于显式 SpacePoint／SpaceVector 的查询转换，不移动已经数值化的对象坐标。fit／auto-size 继续添加最终视口映射；`query.from_canvas` 可反向转换页面位置。

## 可运行示例与输出

```{literalinclude} ../../../../examples/tutorial/geometry/local_coordinates.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![灰色世界坐标轴与蓝色局部坐标轴](../../../../examples/output/tutorial/geometry/local_coordinates.svg)

完整源码：[local_coordinates.py](../../../../examples/tutorial/geometry/local_coordinates.py).

---

[本部分目录](index.md)
