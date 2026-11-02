# 1.1 第一张图

创建一个带方框的“Hello world”标签，并保存为 SVG。主要分两步：
创建绘图对象，再将它们提交到 Canvas。

在仓库根目录用 pyenv 选择 Python 3.12 或更高版本，执行 `uv sync`，再运行 `uv run python -m examples.tutorial.basics.hello_world`。完整源码包含输出目录和 `canvas.save(...)`。此 SVG 示例需要可用的系统字体，无需 TeX 编译器。

## 完整示例

```{literalinclude} ../../../../examples/tutorial/basics/hello_world.py
:language: python
```

## 创建绘图对象

`text("Hello world")` 创建文字标签，并赋给变量 `label`。
`Node(label, position=(30, 15))` 将这个标签放入矩形边框中，边框大小会适应文字。
生成的带框标签赋给变量 `hello`，其中心位于 `(30, 15)`，坐标单位为毫米。

这些调用创建了可用于绘图的对象。创建对象并不会自动将它放到 Canvas 上。

## 提交到 Canvas 并保存

`Canvas(60, 30)` 创建宽 60 mm、高 30 mm 的绘图区域。原点位于左下角，
所以 `(30, 15)` 会将节点放在页面中央。

`canvas.draw(hello)` 将带框标签提交到这个 Canvas。这一步才将它纳入图中：
如果省略这次调用，保存这个 Canvas 得到的将是一张空图。

最后，示例创建输出目录，并调用 `canvas.save(...)`。
SVG 文件会写入 `examples/output/tutorial/basics/hello_world.svg`，
在浏览器中打开它即可看到下方的结果。

## 结果

![矩形边框内的 Hello world 文字标签](../../../../examples/output/tutorial/basics/hello_world.svg)

完整源码：[hello_world.py](../../../../examples/tutorial/basics/hello_world.py).

---

[本部分目录](index.md)
