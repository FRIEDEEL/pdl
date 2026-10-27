# TikZ 源码与 PDF 输出

`Canvas.render("tikz")` 返回独立 TeX 文档字符串，`standalone=False` 返回可嵌入片段，不编译最终 PDF。绘制中 `TeX` 对象的测量仍可能先使用已有 XeLaTeX/dvisvgm 排版流程。

`Canvas.save("figure.tex", backend="tikz")` 默认保存源码并尝试用 XeLaTeX 生成同目录的 `figure.pdf`：

- `tikz_mode="auto"`：默认模式；找到指定编译器就编译，否则仅保留源码。
- `tikz_mode="tex"`：只保存源码。
- `tikz_mode="pdf"`：必须编译；缺少编译器抛出 `FileNotFoundError`。
- `keep_intermediates=False`：默认在临时目录编译，仅复制 PDF；设为 True 时在源码目录保留 aux、log 等产物，失败时也可检查日志。
- `engine="xelatex"`：指定编译器；其他引擎必须兼容文档使用的字体和宏包，不会自动换用其他引擎。

编译工作目录是源码目录，支持相对路径输入；禁用 shell escape，超时 60 秒。编译失败会携带诊断报错，不静默降级；源码保留。旧 PDF 和旧辅助文件不会自动删除，因此跳过或失败不会刷新旧 PDF。TikZ 保存请使用 `.tex` 文件名。

```python
canvas.save("figure.tex", backend="tikz", tikz_mode="auto")
canvas.save("debug.tex", backend="tikz", tikz_mode="pdf", keep_intermediates=True)
```

全部示例复用同一编译辅助函数：

```sh
uv run python -m examples.tools.render_all
uv run python -m examples.tools.render_all --tikz-mode tex
uv run python -m examples.tools.render_all --tikz-mode pdf --keep-intermediates
```

集成测试通过真实 LaTeX 引擎验证编译及默认仅保留 TeX/PDF 的行为。
