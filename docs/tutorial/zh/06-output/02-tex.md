# 6.2 TeX 怎样变成图中的内容

字体和 TeX 测量是 Author 可独立调用的外部工具服务。通过 RendererConfig 或 Canvas typography 上下文，使查询与提交使用同一资源策略。

TeX 缓存包括内容、配置、工具版本和声明的依赖文件内容。几何仍为原生表达时，TikZ 保留源码，SVG 嵌入带命名空间的片段。同一原生 TikZ 文档需要兼容的 TeX 环境；转轮廓时会拒绝不支持的复杂／彩色 SVG。

## 可运行示例与输出

```{literalinclude} ../../../../examples/tutorial/advanced/tex_pipeline.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![公式和按文字尺寸撑开的节点](../../../../examples/output/tutorial/advanced/tex_pipeline.svg)

完整源码：[tex_pipeline.py](../../../../examples/tutorial/advanced/tex_pipeline.py).

---

[本部分目录](index.md)
