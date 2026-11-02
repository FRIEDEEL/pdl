# 2.4 多个子路径与镂空

多个独立子路径可描述孔洞和复合轮廓。nonzero 依据绕数填充，evenodd 依据交叉次数填充；填充规则不会给开放子路径额外添加描边边缘。

`PathGeometry.extend(...)` 拼接可转换为路径的纯几何。先构造几何，再创建 Entity 绘制。Bézier 控制点的仿射映射是精确的；圆／椭圆转路径时采用跨度不超过 45 度的三次近似。

## 可运行示例与输出

```{literalinclude} ../../../../examples/tutorial/advanced/fill_rules.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![左侧 nonzero 填充，右侧 evenodd 填充](../../../../examples/output/tutorial/advanced/fill_rules.svg)

完整源码：[fill_rules.py](../../../../examples/tutorial/advanced/fill_rules.py).

---

[本部分目录](index.md)
