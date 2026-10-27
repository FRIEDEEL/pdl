# 17. 操作可以重叠的集合

Gather 收集已有操作单位，不改变它们所属的 Group 或 Layer。它没有自己的坐标系和继承样式。
同一实例可以同时加入多个 Gather。

```{literalinclude} ../../../examples/tutorial/layout/gathers.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![17. 操作可以重叠的集合](../../../examples/output/tutorial/layout/gathers.svg)

[完整可运行示例](../../../examples/tutorial/layout/gathers.py)

下排是初始捕获。combined 虽然从两个集合收集组件，但其中只包含一次该组件。
平移 combined 时两个单位各移动一次；随后旋转 second 只影响组件，严格遵守调用先后。

添加另一个 Gather 时，将对方当时的成员展开到当前身份集合；之后的增删不会联动。
可使用 add、remove、union、intersection、difference。Gather 本身不能交给 canvas.draw。

选中组内元素时会提升为最外层 Group，并发出 UserWarning。每条命令执行前再次检查归属，
因此先选中、后组合也不会重复变换。members 可以查看实际目标。目标 Group 解散后应重新建立选择。

试试把 marker 加入 second，它就会依次接受两条命令，各执行一次。
