# 生长式流程图

使用 `FlowNode` 表示普通处理框，`Decision` 表示判断菱形，`Terminal`
表示圆形起止节点。这些是可编辑的上层组件，原有不可变 `Node` 接口保持可用。

```{literalinclude} ../examples/flowcharts/growing.py
:language: python
:start-at: start =
:end-before: canvas =
```

![Growing flowchart](../examples/output/flowcharts/growing.svg)

`a.right(b)` 在右侧放置新节点并连接，返回 **b**，便于继续生长。
`left`、`above`、`below` 同理。默认边界间距为 12 mm，文字在渲染时使用最终字体测量。
子节点初始 position 是生长位置上的额外偏移。修改文字、尺寸后重新计算间距；
平移父节点也会移动其生长出的后代，其他分支保留位置。

汇合、回路使用 `connect(existing)`，不会移动已有目标。返回的 `FlowEdge`
允许调整起止端口、`via` 途经点、标签和样式。连线是显式折线，不自动避障。
菱形建议使用上下左右端口。标签位于路径中点旁，密集图仍可能发生重叠。

对根节点调用一次 `canvas.draw(root)`，绘制所有出边可达节点和放置依赖的祖先，
回路不会重复绘制节点。连接先画，节点后画。draw 捕获当前节点和边的状态，
此时不测量字体；之后编辑只影响新的绘制记录。捕获后可通过 Entity 或 Group
变换整个组件，内部节点在捕获前编辑。

运行 `uv run python examples/flowcharts/growing.py`，在
`examples/output/flowcharts/` 生成 SVG、TikZ 和 PDF（PDF 需要 XeLaTeX）。
本阶段通过实际源码和输出检查组件使用体验。[English](flowcharts.md)。
