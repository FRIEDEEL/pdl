# 可编辑流程图

FlowNode 表示普通流程，Decision 表示菱形，Terminal 表示圆形端点。
方向方法 right／left／above／below 放置新的子节点并返回它；默认边界间隔为 12 毫米。
标签的排版尺寸在展开时参与定位。修改标签后，后续捕获会重新计算；移动父节点也移动其生长的后代。

connect(existing) 连接已有节点而不移动它，返回可编辑 FlowEdge。端口、标签、via、style 均可修改。
正交路由根据方向端口生成折线；route="straight" 直接连接，显式 via 覆盖自动折线。
没有避障路由，密集图仍可能重叠。

提交根节点时捕获可达的有向图，允许合并与反馈环；先画连接，再画节点。
展开使用 Canvas 的字体／TeX 策略并固定结果，后续源图修改不影响已有提交。
捕获结果是普通 Entity／Group，可复制、变换和组合。Connection 的端点在创建时数值化，
独立 Connection 不会自动跟随节点。

```{literalinclude} ../examples/flowcharts/growing.py
:language: python
:start-at: start =
:end-before: canvas =
```

![Growing flowchart](../examples/output/flowcharts/growing.svg)

[API](api/flowcharts.md) · [English](flowcharts.md)
