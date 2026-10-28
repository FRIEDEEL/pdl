# 1.1 第一张图

我们先画一个写着 **Hello world** 的方框，保存成 SVG 图片。
这个例子只需要 Python 和 pdl，不需要安装 TeX。

## 准备运行环境

前几章直接在 pdl 仓库中运行。先用 pyenv 选择 Python 3.12 或更高版本，
在终端进入仓库根目录，也就是包含 `pyproject.toml` 的文件夹，然后安装项目和开发工具：

```sh
uv sync
```

这里假定你已经安装了 uv 和适用的 Python 版本。文字会自动使用系统中的
sans-serif 字体，因此不同电脑上的字形可能略有不同。如果提示无法找到默认字体，
需要先让系统能够找到一种 sans-serif 字体。

## 写代码并运行

把下面的代码保存为 `examples/tutorial/basics/hello_world.py`，
也可以直接打开仓库中已有的这个文件。用代码下方的命令运行。

```{literalinclude} ../../../../examples/tutorial/basics/hello_world.py
:language: python
```

运行（在仓库根目录）：

```sh
uv run python examples/tutorial/basics/hello_world.py
```

![hello world](../../../../examples/output/tutorial/basics/hello_world.svg)

[完整源文件](../../../../examples/tutorial/basics/hello_world.py)

用浏览器打开 `examples/output/tutorial/basics/hello_world.svg`。
你应该能看到一个矩形方框，里面写着“Hello world”。
上面展示的就是这个 SVG；如果本地 Markdown 预览里没有图片，先运行一次脚本。
教程图片统一生成到 `examples/output/`，这个目录不提交到 Git。

## 这几行分别做了什么

`Text("Hello world")` 创建文字，`Node(...)` 在文字外面加上方框，
并在文字和边框之间留出一点空隙。你不需要自己计算方框的宽度。

`position=(30, 15)` 指定的是 **Node 的中心位置**：从画布左下角向右 30 mm，
再向上 15 mm。

`Canvas(60, 30)` 创建一块宽 60 mm、高 30 mm 的画布。
在这些例子中，x 向右增大，y 向上增大，坐标和图形尺寸都以毫米为单位。

`canvas.draw(hello)` 把这个 Node 加进图里。仅仅创建物件，它还不会出现在画布上。
`canvas.save(...)` 才把图片写进 SVG 文件。

最后三行用来选择输出文件夹、在必要时创建文件夹，并保存图片。
如果你希望直接保存到终端当前所在的目录，也可以换成
`canvas.save("hello_world.svg")`。

## 自己改一下

把 `"Hello world"` 换成 `"My first drawing"`，重新运行。
方框会随文字变宽，但中心仍然在 `(30, 15)`。
再把位置改成 `position=(30, 22)`，方框就会向上移动。
画布大小不会随之改变，超出画布的部分会被裁掉。

下一章：[画三角形、矩形和圆](02-shapes.md)。

---

[本篇目录](index.md)
