# 4.1 渐变填充与透明度

LinearGradient、RadialGradient 使用有序的不透明 RGB 色标，初始坐标相对对象包围盒归一化。变换同步确定渐变的当前坐标框架，使颜色方向与几何保持一致。

渐变用于填充；原生文字／TeX 使用纯色填充。透明度按叶对象分别生效，重叠成员分别绘制，Group 不建立独立透明合成面。

## 可运行示例与输出

```{literalinclude} ../../../../examples/tutorial/paint/gradients.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![20. 渐变填充与透明度](../../../../examples/output/tutorial/paint/gradients.svg)

```{literalinclude} ../../../../examples/tutorial/paint/opacity.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![Opacity](../../../../examples/output/tutorial/paint/opacity.svg)

完整源码：[gradients.py](../../../../examples/tutorial/paint/gradients.py), [opacity.py](../../../../examples/tutorial/paint/opacity.py).

---

[本部分目录](index.md)
