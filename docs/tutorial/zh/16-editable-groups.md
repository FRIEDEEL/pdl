# 16. 编辑与解散组合

希望将已有实例组成可编辑的整体时，使用 Entity。一个实例最多有一个直接父 Group。
加入已有 Entity 或 Group 时保留世界位置；传入 Drawing 则创建独立的局部实例，与第 9 章一致。

```{literalinclude} ../../../examples/tutorial/layout/editable_groups.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![16. 编辑与解散组合](../../../examples/output/tutorial/layout/editable_groups.svg)

[完整可运行示例](../../../examples/tutorial/layout/editable_groups.py)

左边是编辑前捕获的组合，右边是旋转和平移后的捕获。主体与端口一起移动。
最后 `dismiss()` 解散当前这一层组合，小端口便能独立上移；之前的 draw 记录保持不变。

`group.add(instance)` 将已有实例重新归属到组合；`group.remove(instance)` 移出直接成员。
两者均保留世界位置与有效样式。`dismiss()` 将直接成员提升到父容器，保留内部子 Group。
解散后的空 Group 不再接受新成员。父变换不可逆时无法重新归属，会抛出 ValueError。

子物件的显式样式优先于组默认样式，按整体覆盖。绘制时提交最外层 Group，不能单独提交组内元素。
读取具体端口可以用 `group.child(index)` 或捕获的子元素锚点。

试试先添加第三个零件，旋转后再将它移出。
