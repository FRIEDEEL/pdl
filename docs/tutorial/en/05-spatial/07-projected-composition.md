# 5.7 Projected layers: a material and probe

Place a probe inside the open cylindrical material. For this fixed-view cutaway,
we choose to draw the probe over the material, regardless of world depth. Keep
the background on the left as a reference and assemble the illustration on the right:

```{literalinclude} ../../../../examples/tutorial/spatial/projected_layers.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![Material reference beside a separately projected probe and 2D label](../../../../examples/output/tutorial/spatial/projected_layers.svg)

[Complete runnable source](../../../../examples/tutorial/spatial/projected_layers.py)

## Share a camera, then choose coverage in 2D

Each `Scene3D.project()` creates an ordinary 2D Authoring snapshot. Use the same
camera settings (including target and, for supported perspective geometry,
distance/focal length) and the same world coordinate frame to align snapshots.
Do not independently center or fit each one. Apply the same 2D placement to
related layers, for example by putting them in one Group.

`assembly.add(material_2d)` precedes the probe, so the probe covers it.
Canvas also respects explicit layers; at the same layer, draw order determines
coverage. Neither Group nor Canvas combines the original scenes' depth data.
The ordering is intentional even when one source lies behind another in 3D.

There are two distinct scopes:

| Composition | Visibility behavior |
| --- | --- |
| Supported polygon objects in one BSP scene | Sort and split faces during that projection |
| `sort_faces=False` in one scene | Preserve source object/face order without BSP splitting |
| Independently projected snapshots | Follow 2D layer/draw order, with no cross-scene splitting |

A curved object can internally paint its visible branches or walls in order even
in a manual scene. Manual scene order governs objects, not those internal parts.
`ProjectedScene.reordered()` can reorder current children within a snapshot;
BSP children may be face fragments, not whole original faces.

## Choose where to edit

Change the 3D source when a geometric relationship matters: move the probe base,
change its axis, then project it again with the same camera. Existing snapshots
remain unchanged. Projecting one scene never alters or re-sorts another snapshot.

After projection, ordinary Entity/Group transforms, styling and 2D annotations
are available. The example projects the probe tip through `material_2d.point()`
to attach its label without guessing image coordinates. Translating the complete
Group moves the drawing and label together. Moving only the probe in 2D is also
allowed, but does not update its source 3D position.


[Full material/probe recipe](../07-recipes/02-material-probe.md)

[Part contents](index.md)
