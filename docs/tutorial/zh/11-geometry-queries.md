# 11. 测量一张图

锚点可以先描述关系，不急着算出数字。但有时我们确实需要数值，比如检查一个旋转后
的图形有多宽。这时可以用画布的 query。

```{literalinclude} ../../../examples/tutorial/geometry/queries.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![旋转后的矩形与红色轴对齐包围框](../../../examples/output/tutorial/geometry/queries.svg)

[完整可运行示例](../../../examples/tutorial/geometry/queries.py)

红色矩形是包住旋转后图形的轴对齐边界框。它的边始终平行于世界坐标轴，
不是把原矩形旋转后描一遍。终端还会打印中心 `(30.0, 20.0)`。

`in_space=WORLD` 明确要求作者世界坐标。不写时，结果使用最终 Canvas 坐标，
在 fit 模式或画布映射下，两者可能不同。这里的 bounds 不包含描边宽度。
对于文字，普通 bounds 使用排版框；ink_bounds 则使用可见字形轮廓。

Bounds 提供 left、bottom、right、top、width、height。
它的 anchor 返回数值 Point。要把延迟锚点算成数值，使用
`canvas.query().point(reference, in_space=WORLD)`。

查询不会把目标自动画出来。本例只有显式 draw 才加入图形和红框。
数值结果也是一次快照：之后再改物件，红框不会自动跟随，必须重新查询和构造。

在适配画布中，应先确定绘制列表，再查询最终 Canvas 坐标，因为适配依据这个列表。
`query().from_canvas(...)` 可以把数值转换回作者坐标，但不会恢复锚点依赖。
经过不可逆变换的逆向坐标转换会抛出 ValueError。

## 自己试试

把角度从 30 改为 60 度，重新运行，对比边界框的宽高。
空 Bounds 的 `is_empty=True`，不能取得有效锚点。

接口说明：{py:class}`pdl.Query`、{py:class}`pdl.Bounds`。

---

[上一章：自定义轮廓与曲线](10-paths.md) · [下一章：画布适配](12-viewports.md)
