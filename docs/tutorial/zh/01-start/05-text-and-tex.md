# 1.5 文字与公式

Text 表示普通 Unicode 文字，TeX 解释 LaTeX 源码。参考位置是毫米坐标中的基线点，字号采用 TeX point（1/72.27 英寸）。字体和 TeX 配置参与测量。

查询按需测量，Canvas 提交时固定字体／配置和排版。平移、旋转保留原生描述；正向均匀缩放保留普通 Text，TeX 缩放则变换测量所得轮廓，使固定尺寸也正确缩放。拉伸、剪切及镜像等也不可逆地转成路径。不支持的复杂／彩色 TeX 轮廓会报错。TeX 测量需要 XeLaTeX 和 dvisvgm。

## 可运行示例与输出

```{literalinclude} ../../../../examples/tutorial/text/labels.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![两行不同字号的文字，以及对应基线](../../../../examples/output/tutorial/text/labels.svg)

```{literalinclude} ../../../../examples/tutorial/text/formula.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![用 LaTeX 排版的公式](../../../../examples/output/tutorial/text/formula.svg)

完整源码：[labels.py](../../../../examples/tutorial/text/labels.py), [formula.py](../../../../examples/tutorial/text/formula.py).

---

[本部分目录](index.md)
