# 3.1 把几个物件组合起来复用

Group 是带有有序成员的 Entity，每个成员最多有一个父 Group。变换立即更新成员的世界坐标几何，影响现有成员；之后加入的对象使用其传入时的当前坐标。

成员显式 Style 优先；None 向最近显式设置样式的 Group 回退，再使用自身默认值。加入和退出均保留 None。`group.set_style` 只修改 Group 自己。示例车身继承蓝色，端口保留显式橙色。

原生文字／TeX 需要仅填充样式；Group 提供带描边的形状样式时，应给标签显式指定仅填充 Style。

## 可运行示例与输出

```{literalinclude} ../../../../examples/tutorial/layout/groups.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![同一个组件在两个位置重复使用](../../../../examples/output/tutorial/layout/groups.svg)

完整源码：[groups.py](../../../../examples/tutorial/layout/groups.py).

---

[本部分目录](index.md)
