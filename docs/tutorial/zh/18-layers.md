# 18. 控制图层上下顺序

Layer 只控制覆盖顺序，没有平移或旋转，也不能直接绘制。Canvas 拥有有序图层栈，索引 0 为最底层。

```{literalinclude} ../../../examples/tutorial/layout/layers.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![18. 控制图层上下顺序](../../../examples/output/tutorial/layout/layers.svg)

[完整可运行示例](../../../examples/tutorial/layout/layers.py)

红色虽然先提交，但前景层会让它覆盖金色与蓝色。同层内部保持提交顺序。
set_layer(layer) 与 layer.add(instance) 只分配归属，不自动绘制。

set_layer(1) 在下一次 draw 时解析为 Canvas 当时的索引，随后绑定 Layer 身份。
绘制前需要确定归属时，优先使用 canvas.layers[1]。
insert_before／insert_after 可以在相邻图层之间插层，已有归属不变；
move_before／move_after 调整层序，也会改变已捕获记录的上下关系。

修改对象归属仅影响后续 draw，旧记录保留其 Layer 身份。一个 Layer 只属于一个 Canvas。
单独构造的两个 Layer(1) 是不同身份；需要统一索引入口时使用 Canvas.layers。

Group 整体位于一个 Layer。跨层组合默认提升到成员最高层，也可通过 Group(..., layer=...) 指定。
内部保留原来由下到上的顺序，同层按传入顺序；外部物件不能继续穿插在成员之间。
解散后成员保留组合当前的层，不恢复组合前的归属。

layer.to_gather() 收集当前顶层成员以执行空间操作，包含已分配但未绘制的对象，
不选择旧 Canvas 快照。Gather 可以跨层。对组内元素设置 Layer 时会提升到最外层 Group 并提示。

试试在保存前把 foreground 移到 background 下方。
