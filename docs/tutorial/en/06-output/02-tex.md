# 6.2 How TeX becomes a drawing

Font and TeX measurement are external-tool services available to Author independently of the drawing backend. Use RendererConfig or a Canvas typography context to establish one resource policy for queries and submissions.

TeX caches include content, configuration, tool versions, and declared dependency contents. Native TikZ output retains source when the geometry remains native; SVG embeds a namespaced fragment. One native TikZ document requires compatible TeX environments. Outline conversion rejects unsupported rich/colored SVG rather than discarding content.

## Runnable examples and output

```{literalinclude} ../../../../examples/tutorial/advanced/tex_pipeline.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![A formula inside an automatically measured node](../../../../examples/output/tutorial/advanced/tex_pipeline.svg)

Full source: [tex_pipeline.py](../../../../examples/tutorial/advanced/tex_pipeline.py).

---

[Part contents](index.md)
