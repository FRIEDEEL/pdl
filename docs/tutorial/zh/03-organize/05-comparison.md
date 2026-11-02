# 3.5 Group、Layer 与 Gather：结构、顺序与选择

Group 组织归属，Layer 安排捕获后的覆盖顺序，Gather 显式选择已有对象执行命令。Group 保留成员身份和样式回退，坐标立即更新；Layer 不承担空间变换；Gather 保存允许重叠的成员选择。

对于 `Gather(a, b)` 与 `Gather(b, c)`，B 按调用顺序接受两组操作。一次操作内部去重，分开的操作分别生效；之后通过另一选择执行的修改仍会改变相对位置。

| 概念 | 归属 | 空间编辑 | 样式／绘制 |
| --- | --- | --- | --- |
| Group | 成员最多一个父级 | 一起编辑当前成员 | 显式祖先样式回退 |
| Gather | 无归属，可重叠 | 显式目标，一次操作去重 | 只设置选中对象 |
| Layer | Canvas 顺序身份 | 不变换 | 安排捕获内容的覆盖 |

## 可运行示例与输出

```{literalinclude} ../../../../examples/tutorial/layout/shared_gathers.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![两个重叠 Gather 相互改变对方的内部排列](../../../../examples/output/tutorial/layout/shared_gathers.svg)

完整源码：[shared_gathers.py](../../../../examples/tutorial/layout/shared_gathers.py).

---

[本部分目录](index.md)
