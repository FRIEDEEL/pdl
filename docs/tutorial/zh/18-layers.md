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
insert_below／insert_above 可以在相邻图层之间插层，已有归属不变；
move_below／move_above 调整层序，也会改变已捕获记录的上下关系。

`middle.upper` 返回紧邻上方的 foreground，`middle.lower` 返回紧邻下方的 background。
最顶层的 upper、最底层的 lower，以及尚未加入层栈的 Layer 的相邻层都返回 None。
读取属性不创建新层，插层或移层后再次读取会反映当前顺序。

这里没有“当前活动层”计数器。Layer() 创建独立身份，默认期望插入位置为 0，
不会自动追加到最上方；需要新建相邻层时显式调用 insert_above／insert_below。

修改对象归属仅影响后续 draw，旧记录保留其 Layer 身份。一个 Layer 只属于一个 Canvas。
单独构造的两个 Layer(1) 是不同身份；需要统一索引入口时使用 Canvas.layers。

Group 整体位于一个 Layer。跨层组合默认提升到成员最高层，也可通过 Group(..., layer=...) 指定。
内部保留原来由下到上的顺序，同层按传入顺序；外部物件不能继续穿插在成员之间。
解散后成员保留组合当前的层，不恢复组合前的归属。

layer.to_gather() 收集当前顶层成员以执行空间操作，包含已分配但未绘制的对象，
不选择旧 Canvas 快照。Gather 可以跨层。对组内元素设置 Layer 时会提升到最外层 Group 并提示。

试试在保存前把 foreground 移到 background 下方。


## 三明治：为什么同时需要 Group 和 Gather

![Layer、Gather 与 Group 的三种结果](../../../examples/output/composition/sandwich.svg)

[完整可运行源码](../../../examples/composition/sandwich.py)

1. 底板、中间物件、盖板位于三个 Layer。每块板本身都是 Group，螺钉和文字跟随板一起移动。
2. Gather 跨层收集底板和盖板，一起右移；中间物件保持原位，仍夹在两者之间。
3. 改用 Group 组合底板和盖板后，二者整体提升到最高成员层，底板会盖住中间物件的下缘。

想保持三明治结构并共同操作，用 Gather；想将选中部分变成不可穿插的整体，用 Group。
