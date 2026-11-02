# 1.1 第一张图

创建方框与普通文字，加入 Canvas，再保存为 SVG。`rectangle(...)`、`text(...)` 等绘图工厂返回 Entity，由实体持有几何和可选 Style。

在仓库根目录用 pyenv 选择 Python 3.12 或更高版本，执行 `uv sync`，再运行 `uv run python -m examples.tutorial.basics.hello_world`。完整源码包含输出目录和 `canvas.save(...)`。此 SVG 示例需要可用的系统字体，无需 TeX 编译器。

## 可运行示例与输出

```{literalinclude} ../../../../examples/tutorial/basics/hello_world.py
:language: python
```

![hello world](../../../../examples/output/tutorial/basics/hello_world.svg)

完整源码：[hello_world.py](../../../../examples/tutorial/basics/hello_world.py).

---

[本部分目录](index.md)
