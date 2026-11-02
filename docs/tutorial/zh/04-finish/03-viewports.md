# 4.3 让内容放进画布

clip 保留固定视口；fit 在固定尺寸中均匀缩放并居中内容；auto_size 根据内容确定尺寸，加上 padding 并平移。拟合使用逻辑几何／排版边界及保守描边余量。

最终视口处理使用捕获状态，线宽仍以输出毫米计。padding 需要留下可拟合的空间；空的 auto_size 输出仍是一张有效的小画布。

## 可运行示例与输出

```{literalinclude} ../../../../examples/tutorial/advanced/viewport_clip.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![固定视口裁掉超出的圆](../../../../examples/output/tutorial/advanced/viewport_clip.svg)

```{literalinclude} ../../../../examples/tutorial/advanced/viewport_fit.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![fit 把内容缩放到固定视口内](../../../../examples/output/tutorial/advanced/viewport_fit.svg)

```{literalinclude} ../../../../examples/tutorial/advanced/viewport_auto_size.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![auto_size 保持比例并改变画布尺寸](../../../../examples/output/tutorial/advanced/viewport_auto_size.svg)

完整源码：[viewport_clip.py](../../../../examples/tutorial/advanced/viewport_clip.py), [viewport_fit.py](../../../../examples/tutorial/advanced/viewport_fit.py), [viewport_auto_size.py](../../../../examples/tutorial/advanced/viewport_auto_size.py).

---

[本部分目录](index.md)
