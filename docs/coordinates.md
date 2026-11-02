# World coordinates, explicit frames, and queries

Ordinary Entities store current world geometry. Frame describes an explicit
origin and two world basis vectors. Call point((x, y)), vector(...), or
coordinates(world_point) to obtain fixed values. Frame.child(affine) creates a
new world description in that basis without a live object attachment.

Default rotation/scaling uses Entity.reference; origin chooses another pivot.
move_to aligns the reference, and anchor selects a logical bounds position.
Changing a reference does not move geometry. Anchors use world-aligned logical
bounds excluding stroke. Text references its baseline; layout bounds need fonts.

Pure Point/Frame values are not submitted to Canvas. frame_axes creates an
explicit drawing Group that can be selected with a shape in Gather. Its frame
property supplies the transformed current basis. Ordinary shapes have no implicit
frame/space properties.

Canvas queries default to final page coordinates. in_space=WORLD selects Author
coordinates; another Frame requests conversion. canvas.map(WORLD, affine)
sets the final page mapping, followed by fit/auto-size viewport policy. Overrides
for other Frames affect explicit SpacePoint/SpaceVector queries and do not move
already numerical shapes. query.from_canvas supplies the inverse conversion.

```{literalinclude} ../examples/tutorial/geometry/local_coordinates.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```



[Explicit axes lesson](tutorial/en/03-organize/07-frames.md) · [Query API](api/coordinates.md)
