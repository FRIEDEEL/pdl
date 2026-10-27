# 6. 移动、旋转和缩放

前面的例子通过构造函数里的坐标放置图形。
如果想用方法调用移动已有物件，可以把它放进 {py:class}`pdl.Entity`。

## 移动矩形

```{literalinclude} ../../../examples/tutorial/geometry/translation.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![原位置的灰色轮廓和移动后的矩形](../../../examples/output/tutorial/geometry/translation.svg)

[完整可运行示例](../../../examples/tutorial/geometry/translation.py)

`translate(25, 10)` 把矩形向右移动 25 mm、向上移动 10 mm，并修改这个 Entity。
第一次 draw 已经捕获旧状态，所以灰色轮廓留在原处；第二次 draw 记录移动后的状态。
这样不用自己重算顶点，也能得到一张前后对照图。

`move_to((x, y))` 的含义不同：它把变换后局部边界的中心放到目标位置，
而不是在现有位置上增加一段位移。

## 选择旋转中心

```{literalinclude} ../../../examples/tutorial/geometry/rotation.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![绕红色中心点旋转后的矩形](../../../examples/output/tutorial/geometry/rotation.svg)

[完整可运行示例](../../../examples/tutorial/geometry/rotation.py)

红点就是旋转中心 `(25, 20)`，正角度表示逆时针。
灰色轮廓保留原位置。如果不写 `center=...`，旋转中心默认是世界原点，
不是物件自身的中心；离开原点的矩形旋转后，位置也会改变。

## 把圆拉成椭圆

```{literalinclude} ../../../examples/tutorial/geometry/scaling.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![圆经过不等比例缩放形成椭圆](../../../examples/output/tutorial/geometry/scaling.svg)

[完整可运行示例](../../../examples/tutorial/geometry/scaling.py)

水平方向放大 2 倍，竖直方向缩为 0.75 倍，圆就变成了椭圆。
只传一个比例时，两个方向等比例缩放。`center` 指定保持不动的中心。
图形和文字都会缩放，但描边宽度仍使用最终画布上的毫米值。

这些方法返回同一个 Entity，因此可以连续调用。后一次操作在作者世界坐标中作用于
已有放置：先移动再旋转，通常不同于先旋转再移动。
`reflect(angle, origin=...)` 可以绕一条直线镜像；剪切则可以通过
`entity.transform(Transform.shear(...))` 完成。

## 自己试试

把角度改成 `-30`，再把旋转中心改成 `(15, 15)`。
保留灰色轮廓，分别观察方向和位置发生了什么变化。

接口说明：{py:class}`pdl.Entity`、{py:class}`pdl.Transform`。

---

[上一章：文字与公式](05-text-and-tex.md) · [下一章：局部坐标系](07-coordinate-systems.md)
