# 2. 构造与变换图形

第一部分介绍了创建绘图对象、将它们提交到 Canvas。在构造路径和变换形状之前，
先看看这些对象内部包含什么。本部分引入三个概念：**Geometry**、**Style** 和 **Entity**。

## 调用 rectangle() 时发生了什么？

[第一部分的形状示例](../01-start/02-shapes.md) 包含这一行：

```{literalinclude} ../../../../examples/tutorial/basics/shapes.py
:language: python
:start-at: rectangle_entity =
:end-before: circle_entity =
```

`rectangle` 是工厂函数。它先创建一个 `Rectangle` 几何描述，左下角位于 `(40, 10)`，
宽 25 mm、高 20 mm；再创建一个持有该描述的 `Entity`，并返回这个 Entity。
因此，变量 `rectangle_entity` 指向的是一个可以编辑、可以通过
`canvas.draw(rectangle_entity)` 提交的绘图对象。

这个函数不会向 Canvas 提交任何内容。省略 `style=` 时，Entity 的 `style` 保持为 `None`，
函数不会为它创建显式的 Style。独立矩形未设置样式时，绘制时使用默认的黑色轮廓，不填充内部。

## Geometry、Style 和 Entity

| 概念 | 描述什么 | 本例中的对应内容 |
| --- | --- | --- |
| Geometry | 当前形状、尺寸和位置，不包含绘制样式 | 包含原点、宽度和高度的 `Rectangle` |
| Style | 描边、填充、线宽等绘制设置 | 橙色填充和 0.5 mm 宽的轮廓 |
| Entity | 持有几何和可选 Style 的绘图对象，并提供移动等操作 | 传给 `canvas.draw(...)` 的对象 |

Geometry 是对几何描述的统称，并不要求实例化一个共同的类。本例中，具体的几何类是
`Rectangle`。小写的 `rectangle(...)` 创建绘图 Entity，大写的 `Rectangle(...)` 只创建几何描述。

下面两种构造方式会得到等价的矩形：

```{literalinclude} ../../../../examples/tutorial/geometry/object_model.py
:language: python
:start-after: "# construction-start"
:end-before: "# construction-end"
```

`Entity(geometry)` 直接持有传入的几何，可以通过 `explicit_rectangle.geometry` 访问。
它不会复制几何，也不会向 Canvas 提交。两种构造方式都会让可选的 Style 保持未设置。
裸 `Rectangle` 描述可以用于数值查询；绘制前，需要将它放入 Entity。

## 加上 Style

在[第一部分的配色示例](../01-start/03-stroke-and-fill.md) 中，
你通过 `canvas.draw(rectangle_entity, orange)` 传入橙色 Style。
也可以将这个 Style 保存在绘图对象上，既可以使用工厂，也可以直接构造：

```{literalinclude} ../../../../examples/tutorial/geometry/object_model.py
:language: python
:start-after: "# style-start"
:end-before: "# style-end"
```

`orange` 描述绘制样式，`geometry` 描述矩形。Entity `editable` 持有这两者：
`editable.geometry` 是传入的 Rectangle，`editable.style` 是传入的 Style。
工厂函数在一次调用中完成同样的包装；它的结果具有等价的几何和样式，
但它是另一个对象，持有自己单独创建的几何描述。

Style 是不可变值。要改变 Entity 的绘制样式，应创建另一个 Style，并传给 `set_style(...)`。
Entity 未设置 Style，与 Style 内部的 `stroke=None` 或 `fill=None` 含义不同：
后两者明确关闭轮廓或填充。传给 `canvas.draw(...)` 的 Style 只用于该次提交，
不会改变源 Entity 保存的 Style。

## draw() 拓印当前状态

可以将 `canvas.draw(editable)` 理解为在 Canvas 上进行一次拓印。
调用时，它捕获对象当时的几何和实际绘制样式。之后，你仍然可以编辑源 Entity、
它的几何描述或赋给它的 Style，但这些修改不会改变 Canvas 上已经留下的拓印。
保存 Canvas 时使用的是已经提交的记录，不会重新读取源对象。

下面对同一个 Entity 调用两次 `draw`，并在两次调用之间进行编辑：

```{literalinclude} ../../../../examples/tutorial/geometry/object_model.py
:language: python
:start-after: "# capture-start"
:end-before: "# capture-end"
```

第一次调用记录位于 `(40, 10)`、宽 25 mm、高 20 mm 的橙色矩形。
随后，`geometry.width = 15` 修改源 Entity 持有的几何描述；
`translate(30, 15)` 将该 Entity 向右移动 30 mm、向上移动 15 mm；
`set_style` 将其绘制样式替换为蓝色。这些修改都不会改变第一次提交的记录。
只有第二次 `draw` 才会加入位于 `(70, 25)` 的较窄蓝色矩形。
如果省略第二次调用，无论之后怎样编辑源对象，保存的图中都只有第一次的橙色矩形。

![同一 Entity 的第一次橙色拓印和第二次较窄的蓝色拓印](../../../../examples/output/tutorial/geometry/object_model.svg)

完整源码：[object_model.py](../../../../examples/tutorial/geometry/object_model.py)。
运行命令：`uv run python -m examples.tutorial.geometry.object_model`。
[复制与捕获](03-copy-and-capture.md) 会进一步说明独立的可编辑副本与提交捕获。

## 本部分内容

```{toctree}
:maxdepth: 1

01-paths
02-transforms
03-copy-and-capture
04-fill-rules
```

[教程目录](../index.md)
