# 世界坐标、显式 Frame 与查询

普通 Entity 保存当前世界几何。Frame 描述一个原点和两个世界基向量，显式创建后调用
`point((x,y))`、`vector(...)`、`coordinates(world_point)` 取得固定数值。
`Frame.child(affine)` 在当前基下创建新的世界描述，不产生对象间的持续附着。

默认旋转／缩放使用 Entity.reference，`origin=` 可指定支点；`move_to` 对齐参考点，
`anchor=` 可选择包围盒位置。改变参考点不会移动对象。锚点使用世界轴对齐逻辑边界，
不包含描边；文字参考基线，排版边界需要字体测量。

纯 Point／Frame 不提交给 Canvas。`frame_axes(frame)` 创建显式坐标轴实体，支持与图形一起放入 Gather；
其 `.frame` 提供变换后的当前基向量。普通图形没有隐式 `.frame` 或 `.space`。

Canvas.query 默认返回最终页面坐标。`in_space=WORLD` 返回 Author 坐标，指定其他 Frame 则转换到该坐标系。
`canvas.map(WORLD, affine)` 设置最终页面映射，fit／auto_size 再决定视口。
对其他 Frame 的 map 覆盖只影响显式 SpacePoint／SpaceVector 查询，不会移动已经数值化的形状。
`query.from_canvas` 提供反向转换。

```{literalinclude} ../examples/tutorial/geometry/local_coordinates.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```



[显式坐标轴示例](tutorial/zh/03-organize/07-frames.md) · [查询 API](api/coordinates.md) · [English](coordinates.md)
