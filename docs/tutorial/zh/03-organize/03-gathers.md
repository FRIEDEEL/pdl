# 3.3 操作可以重叠的集合

Gather 显式收集 Entity 身份，不建立归属或样式继承。它可以选择整个 Group，也可直接选择成员。一次变换中重叠选中的 Group／成员只处理一次。

`Gather.set_style` 对恰好选中的对象调用 set_style。需要统一修改成员时，显式收集成员。可展开 members 或使用并集／交集／差集组合选择；Gather 本身不是可作为成员的 Entity。

## 可运行示例与输出

```{literalinclude} ../../../../examples/tutorial/layout/gathers.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![17. 操作可以重叠的集合](../../../../examples/output/tutorial/layout/gathers.svg)

完整源码：[gathers.py](../../../../examples/tutorial/layout/gathers.py).

---

[本部分目录](index.md)
