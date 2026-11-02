# 1.3 描边与填充

Style 是不可变的完整样式值。`stroke=None` 关闭描边，`fill=None` 关闭填充。线宽采用最终输出中的毫米，RGB 通道范围为 [0, 1]。原生文字与 TeX 使用纯色填充，并关闭描边。

可通过工厂的 `style=` 或 `set_style` 设置实体样式。`Canvas.draw(entity, style)` 仅覆盖本次提交，源实体保持原样。未指定的实体样式仍为 None，需要时再解析默认值。

## 可运行示例与输出

```{literalinclude} ../../../../examples/tutorial/basics/stroke.py
:language: python
:start-at: from pdl import
:end-before: output =
```

![stroke](../../../../examples/output/tutorial/basics/stroke.svg)

```{literalinclude} ../../../../examples/tutorial/basics/fill.py
:language: python
:start-at: from pdl import
:end-before: output =
```

![fill](../../../../examples/output/tutorial/basics/fill.svg)

```{literalinclude} ../../../../examples/tutorial/basics/fill_only.py
:language: python
:start-at: from pdl import
:end-before: output =
```

![fill only](../../../../examples/output/tutorial/basics/fill_only.svg)

```{literalinclude} ../../../../examples/tutorial/basics/colored_shapes.py
:language: python
:start-at: from pdl import
:end-before: output =
```

![colored shapes](../../../../examples/output/tutorial/basics/colored_shapes.svg)

完整源码：[stroke.py](../../../../examples/tutorial/basics/stroke.py), [fill.py](../../../../examples/tutorial/basics/fill.py), [fill_only.py](../../../../examples/tutorial/basics/fill_only.py), [colored_shapes.py](../../../../examples/tutorial/basics/colored_shapes.py).

---

[本部分目录](index.md)
