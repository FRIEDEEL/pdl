# 12. 让内容放进画布

画布可以保持固定窗口、把内容缩放进固定尺寸，也可以根据内容自己决定大小。
用相同的矩形和圆比较这三种方式。

## 固定窗口：clip

```{literalinclude} ../../../examples/tutorial/advanced/viewport_clip.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![固定视口裁掉超出的圆](../../../examples/output/tutorial/advanced/viewport_clip.svg)

[完整可运行示例](../../../examples/tutorial/advanced/viewport_clip.py)

圆的大部分超出了画布右边缘 60 mm 的位置。
clip 是默认模式，不会为了让物件可见而移动或缩小它们；此模式下 padding 不起作用。

## 缩放到固定尺寸：fit

```{literalinclude} ../../../examples/tutorial/advanced/viewport_fit.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![fit 把内容缩放到固定视口内](../../../examples/output/tutorial/advanced/viewport_fit.svg)

[完整可运行示例](../../../examples/tutorial/advanced/viewport_fit.py)

fit 保持画布为 60 × 40 mm，把内容等比例缩放并居中，留出指定边距。
矩形和圆之间的相对安排不变。

## 根据内容决定大小：auto_size

```{literalinclude} ../../../examples/tutorial/advanced/viewport_auto_size.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![auto_size 保持比例并改变画布尺寸](../../../examples/output/tutorial/advanced/viewport_auto_size.svg)

[完整可运行示例](../../../examples/tutorial/advanced/viewport_auto_size.py)

auto_size 保持图形比例，根据内容和边距确定输出尺寸。
传入的宽高不会限制结果；也可以直接写 `Canvas(mode="auto_size", padding=4)`。

文字会跟随几何缩放，描边宽度仍使用最终画布毫米。
适配使用排版边界和保守的描边余量，不是精确的着色轮廓，部分物件周围可能留出更多空间。

## 自己试试

在三个例子里分别增大圆心的 x 坐标。clip 下圆进一步移出窗口；
fit 下内容缩小；auto_size 下画布变宽。
如果要查询最终 Canvas 位置，应先确定绘制列表。

接口说明：{py:class}`pdl.Canvas`。

---

[上一章：几何查询](11-geometry-queries.md) · [下一章：从物件到图片](13-rendering.md)
