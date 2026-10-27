# 15. 多个子路径与镂空

一个 Path 可以包含几段互不相连的轮廓。哪些内部区域会被填色，由填充规则决定。
我们先把两个同心圆合进一条路径。

```{literalinclude} ../../../examples/tutorial/advanced/fill_rules.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![左侧 nonzero 填充，右侧 evenodd 填充](../../../examples/output/tutorial/advanced/fill_rules.svg)

[完整可运行示例](../../../examples/tutorial/advanced/fill_rules.py)

extend 把两个圆分别追加为独立子路径，不在它们之间画连接线。
两个圆的绕行方向相同：左侧使用默认 nonzero 规则，中心也会填满；
右侧使用 evenodd 规则，穿过两道边界后又回到外部，所以中间留出洞。

规则只影响填充，两个圆的轮廓仍然都有描边。
extend 转换圆时使用三次曲线近似，所以这里的 Path 不再包含两个独立的原生 Circle。

使用 nonzero 时，把内侧轮廓的绕行方向反过来也可以形成洞。
关键是穿越边界的次数和方向，不是哪条子路径最后创建。
这与两个独立 draw 之间的遮挡顺序是不同的概念。

## 自己试试

把两个样式都改成 fill_rule="evenodd"，确认两边都有洞，再缩小内圆半径。
两次绘制复用同一条捕获的路径，只是放置和样式不同。

接口说明：{py:meth}`pdl.Path.extend`、{py:class}`pdl.Style`。

---

[上一章：TeX 渲染](14-tex-rendering.md)
