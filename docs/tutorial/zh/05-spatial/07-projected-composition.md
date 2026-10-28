# 5.7 投影图层：材料与 probe

在开放的圆柱形材料中放入 probe。对于这张固定视角的剖面示意图，
我们指定 probe 覆盖在材料前面，不依赖世界深度。左侧保留材料背景作为参考，右侧完成组合：

```{literalinclude} ../../../../examples/tutorial/spatial/projected_layers.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![材料参考与独立投影的 probe、二维标注并排展示](../../../../examples/output/tutorial/spatial/projected_layers.svg)

[完整可运行源码](../../../../examples/tutorial/spatial/projected_layers.py)

## 共用相机，在二维决定覆盖

每次 `Scene3D.project()` 都生成普通的二维 Authoring 快照。
使用相同相机设置（包括 target；支持透视的几何还包括 distance、focal_length）
和同一世界坐标约定，可以使不同快照对齐。不要分别对每张快照居中或适配尺寸。
相关图层后续也应应用相同的二维放置，例如放入同一个 Group。

`assembly.add(material_2d)` 先于 probe，因此 probe 覆盖材料。
Canvas 同时遵循显式图层；在同一图层内，绘制顺序决定覆盖。
Group 和 Canvas 都不合并原始场景的深度数据。即使某个源对象在三维中更远，
也可以指定其二维投影覆盖在前面。

这里有几种不同的处理范围：

| 组合方式 | 遮挡行为 |
| --- | --- |
| 同一 BSP 场景中的受支持多边形对象 | 在该次投影内排序并切分面 |
| 同一场景设置 `sort_faces=False` | 保留源对象／面顺序，不做 BSP 切分 |
| 独立投影的快照 | 按二维图层／绘制顺序覆盖，不跨场景切分 |

即使场景使用手动顺序，曲面对象内部仍可以按顺序绘制自身的可见分支或侧壁。
场景手动顺序控制对象之间的关系，不展开这些内部部件。
`ProjectedScene.reordered()` 可以重排一个快照的当前子项；
BSP 子项可能是面片段，不一定是原始整面。

## 选择在哪一层修改

几何关系重要时修改三维源对象：移动 probe 底点、改变轴向，再用相同相机重新投影。
已有快照保持不变；投影某个场景不会修改或重排另一个快照。

投影后，可以使用普通 Entity／Group 变换、样式和二维标注。
示例通过 `material_2d.point()` 投影 probe 顶点，放置标注时无需猜测图像坐标。
移动整个 Group，会让图形和标注一起移动。也允许仅在二维移动 probe，
但这不会反向更新其三维源位置。


[完整材料／probe 配方](../07-recipes/02-material-probe.md)

[本篇目录](index.md)
