# 3.1 把几个物件组合起来复用

我们用矩形画零件主体，用小圆画连接端口。
现在想放两个这样的零件，并把其中一个旋转，不再分别计算每个部分的位置。

```{literalinclude} ../../../../examples/tutorial/layout/groups.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![同一个组件在两个位置重复使用](../../../../examples/output/tutorial/layout/groups.svg)

[完整可运行示例](../../../../examples/tutorial/layout/groups.py)

`Group((body, port))` 管理传入的已有对象，加入时保持世界摆放。
变换整个 Group 时，主体和端口一起变化。`copy()` 创建成员独立的新组。

first 是平移后的副本；second 显式围绕世界原点旋转，再平移。原始组合不变。
成员的显式样式优先，否则继承组默认样式；样式按整体覆盖，不逐字段合并。

绘制时提交最外层 Group。`second.child(1)` 返回端口的捕获描述，可用于锚点和连接，
不会单独把端口画出来。

## 自己试试

创建第三个副本并移到其他位置，再只修改其成员，确认其他副本不变。

接口说明：{py:class}`pdl.Group`、{py:meth}`pdl.Entity.copy`、{py:meth}`pdl.Group.child`。


---

[本篇目录](index.md)
