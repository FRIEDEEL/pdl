# 7.2 材料与 probe

较大的示例按具名部件构建：后方材料侧壁、明确绘制的平面底部截面、probe，
最后添加二维引线和文字。末幅在投影前修改 probe 的三维位置和方向；
浅色首幅保留材料背景作对照。

![材料背景、组合后的剖面示意图以及调整后的 probe](../../../../examples/output/spatial/material_probe.svg)

[完整源码](../../../../examples/spatial/material_probe.py)；运行
`uv run python -m examples.spatial.material_probe` 生成 SVG、TikZ 和 PDF。
修改 `make_material`、`make_probe` 与 `make_cutaway` 即可调整几何和绘制顺序。
底部截面使用 Plane3D 单独绘制，不是 CylinderSurface 自动生成的端盖，也不是实体布尔运算结果。

这个配方不会自动隐藏 probe 被材料挡住的部分。需要时将 probe 拆成前后图层，
或在要求真实多边形遮挡时使用同一个受支持的 BSP 场景。
改变相机方向后，应重新检查预期绘制顺序。这是一套可编辑矢量插图流程，
没有跨快照共享的深度缓冲或自动实体剖切。

[本篇目录](index.md)
