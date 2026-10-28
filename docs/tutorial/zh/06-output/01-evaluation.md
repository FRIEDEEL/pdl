# 6.1 从对象到图像

Author 是唯一的绘图模型。锚点和定位操作在调用时取得数值结果；文字查询使用当前
字体或 TeX 测量环境，不等待最终渲染。

`canvas.draw(object)` 捕获当前状态，并使用画布配置固定文字度量。后续编辑与渲染时
字体覆盖不重新布局旧记录。需要新状态时再次 draw。后端接收普通图形、文字、图片和
组的捕获描述，没有另一套 resolved 场景。

## 保留固定结果

```{literalinclude} ../../../../examples/tutorial/advanced/snapshots.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![原标签与移动后的标签](../../../../examples/output/tutorial/advanced/snapshots.svg)

[完整可运行示例](../../../../examples/tutorial/advanced/snapshots.py)

`canvas.snapshot(label)` 不提交绘制，而是返回作者坐标中的普通 Drawing，包含固定布局。
第二张画布可以直接绘制它：

![固定的原标签](../../../../examples/output/tutorial/advanced/snapshots-copy.svg)

原生文字输出仍需要字体或 TeX 资源。SVG 查看器和 LaTeX 的字形排版可能存在差异，
固定布局不承诺逐像素相同。

## 选择输出

`canvas.render("svg")` 返回 XML，`canvas.render("tikz")` 返回 TeX 源码。
`save` 保存输出并可选编译 TikZ PDF。画布适配和资源收集依赖最终提交列表；
绘制顺序与锚点计算顺序独立。

接口：{py:meth}`pdl.Canvas.snapshot`、{py:meth}`pdl.Canvas.render`。
参见 [TikZ 输出](../../../tikz-output_zh.md)。

---

[本部分目录](index.md)
