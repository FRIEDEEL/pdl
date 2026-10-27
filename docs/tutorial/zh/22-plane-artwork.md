# 22. 把图案放进平面

平面可以把局部二维图案带入三维。这里对比同一底板与原生文字在平面倾斜前后的效果。
文字的字形会与底板一起变形，不会作为始终朝向读者的标签显示。

```{literalinclude} ../../../examples/tutorial/spatial/plane_text.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![平放与倾斜平面上的原生文字](../../../examples/output/tutorial/spatial/plane_text.svg)

[完整可运行示例](../../../examples/tutorial/spatial/plane_text.py)

`Plane3D()` 默认原点为世界原点，u 沿 +x、v 沿 +y，局部 `(x, y)` 对应
`origin + x*u + y*v`，长度为毫米。两个独立基向量也可以包含缩放或剪切。
`transformed()` 返回新平面。按右手定则先绕 +x 倾斜，再绕 +z 转向，因为矩阵从右侧先作用。
俯视相机让未变换坐标图正面朝向读者。

`plane.place(artwork)` 描述无限平面内的有限图案，不会把无限平面本身画出来，
也不裁切图案或按场景光源自动改色。投影仿射矩阵同时作用于底板几何、文字基线与字形。
SVG 使用完整矩阵，原生 TikZ 使用 `transform shape`，不需要转字形轮廓或栅格贴图。
Node 的文字居中在后续二维求值中完成，再应用平面变换。

下方说明文字在投影后加入，保持正面。图案中的 Node 用 `Style(stroke=None)` 隐藏框，
只保留居中文字。图案需自行控制在预期边界内，目前不提供裁切。
平面完全侧立时坐标图退化，原生文字会省略，不会恢复成朝向读者的可读标签。
透视映射及文字矢量轮廓见[第 24 章](24-perspective.md)。

试着把倾角从 55 度改为 20 度：平面压缩变小，独立绘制的说明文字形状不变。

[上一章：三维投影](21-project-3d.md) · [下一章：D10 面数字](23-d10.md)
