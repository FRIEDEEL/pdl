# 3.2 编辑与解散组合

通过 add、remove、dismiss 编辑 Group。归属变化保留当前世界几何；dismiss 返回解除归属的成员，其样式根据显式值和新的归属重新解析。

直接修改成员只影响该成员；对 Group 变换则编辑现有整组对象，转换失败不会留下部分修改。Canvas 提交独立捕获当前结果。

## 可运行示例与输出

```{literalinclude} ../../../../examples/tutorial/layout/editable_groups.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![16. 编辑与解散组合](../../../../examples/output/tutorial/layout/editable_groups.svg)

完整源码：[editable_groups.py](../../../../examples/tutorial/layout/editable_groups.py).

---

[本部分目录](index.md)
