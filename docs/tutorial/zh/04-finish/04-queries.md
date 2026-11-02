# 4.4 测量一张图

查询立即返回数字。Entity 的边界／锚点使用 Author 世界坐标，Canvas.query 默认返回最终页面坐标。传入 `in_space=WORLD` 可取得 Author 结果，也可指定显式 Frame 转换。

文字逻辑边界包含排版进位和空白，ink_bounds 会请求字形轮廓。查询可触发测量，但不会提交对象；可用返回值构造参考线或其他实体。

空的 fit／auto-size Canvas 会预测被查询对象提交后的摆放；已有绘图时则使用当前页面映射。
可用 `canvas.viewport().output_transform` 查看世界坐标到页面的映射。

## 可运行示例与输出

```{literalinclude} ../../../../examples/tutorial/geometry/queries.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![旋转后的矩形与红色轴对齐包围框](../../../../examples/output/tutorial/geometry/queries.svg)

完整源码：[queries.py](../../../../examples/tutorial/geometry/queries.py).

---

[本部分目录](index.md)
