# 20. 渐变填充与透明度

渐变可以替换 Style.fill 中的纯色 Color。先定义色标，再选择线性方向或径向中心与半径。

```{literalinclude} ../../../examples/tutorial/paint/gradients.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![20. 渐变填充与透明度](../../../examples/output/tutorial/paint/gradients.svg)

[完整可运行示例](../../../examples/tutorial/paint/gradients.py)

色标位置必须从 0 到 1 严格递增。浅色色标位于 0.4，因此亮带不在正中。
LinearGradient 默认从左到右，方块显式使用左下到右上的方向。

坐标按每个叶子形状的局部几何边界归一化：(0, 0) 是左下，(1, 1) 是右上。
上方长条展示了相同渐变随对象旋转的效果。Group 共享的填充会分别映射到每个叶子，
不会横跨组合整体边界。

RadialGradient 默认中心 (0.5, 0.5)、半径 0.5。非正方形边界会得到椭圆渐变。
超出端点或半径后保持最近端点颜色。目前只支持不透明 RGB 色标、端点延展和填充渐变；
原生 Text／TeX 仍要求纯色。SVG 使用原生渐变资源；TikZ 使用 PDF 函数渐变，需要兼容的
PDF 阅读与打印流程。参见 [PGF 渐变手册](https://tikz.dev/base-shadings)。

试试移动中间色标、反转方向，或将径向中心改为 (0.3, 0.7)。

## 逐对象透明度

Gather.set_opacity 对选中目标执行命令。两个圆各为 50% 不透明度，重叠处合成为 75%。
这不是先合成整组再设置透明度；组内显式样式仍保留优先级。

```{literalinclude} ../../../examples/tutorial/paint/opacity.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![Opacity](../../../examples/output/tutorial/paint/opacity.svg)

[Source](../../../examples/tutorial/paint/opacity.py)
