# 3. Outlines and fills

A circle tells pdl where its boundary is. A `Style` tells pdl how to paint it.
We will keep the same circle and change one part of its appearance at a time.

## Give the outline a color

```{literalinclude} ../../../examples/tutorial/basics/stroke.py
:language: python
:start-at: from pdl import
:end-before: output =
```

![stroke](../../../examples/output/tutorial/basics/stroke.svg)

[Source file](../../../examples/tutorial/basics/stroke.py)

`stroke` is the outline color. `line_width=0.5` makes that outline 0.5 mm wide;
it does not change the circle's radius. The stroke is centered on the boundary.
The default line width is 1 mm, so this outline is thinner than the ones in the
previous chapter.

`Color(red, green, blue)` takes three numbers from 0 to 1. For example,
`Color(1, 0, 0)` is red, `Color(0, 0, 0)` is black, and `Color(1, 1, 1)` is white.
Our blue uses more blue than red or green.

## Fill the inside too

Keep the blue outline and add a light blue fill:

```{literalinclude} ../../../examples/tutorial/basics/fill.py
:language: python
:start-at: from pdl import
:end-before: output =
```

![fill](../../../examples/output/tutorial/basics/fill.svg)

[Source file](../../../examples/tutorial/basics/fill.py)

The only changes are the new `light_blue` color and `fill=light_blue` in the
style. `stroke` and `fill` are independent: one paints the outline, the other
paints the inside.

## Remove the outline

To draw only the filled disk, set `stroke=None`:

```{literalinclude} ../../../examples/tutorial/basics/fill_only.py
:language: python
:start-at: from pdl import
:end-before: output =
```

![fill only](../../../examples/output/tutorial/basics/fill_only.svg)

[Source file](../../../examples/tutorial/basics/fill_only.py)

`None` turns the outline off. It is different from a white outline, which
would still paint over whatever was underneath it. Similarly, `fill=None`
leaves the inside unpainted; it does not fill it with white. That is already
the default, so the first circle in this chapter did not need `fill=None`.

## Use styles on the three shapes

The same style options work for polygons and rectangles. Here is the drawing
from the previous chapter with a different style on each shape:

```{literalinclude} ../../../examples/tutorial/basics/colored_shapes.py
:language: python
:start-at: from pdl import
:end-before: output =
```

![colored shapes](../../../examples/output/tutorial/basics/colored_shapes.svg)

[Source file](../../../examples/tutorial/basics/colored_shapes.py)

The triangle has only a blue outline. The rectangle has an orange fill and
the default black outline. The circle has a green fill and no outline.
Naming styles separately keeps the shape definitions easy to read and lets
you use the same style on several objects.

## Try a small change

In `fill.py`, change `line_width=0.5` to `line_width=2` and rerun the script.
The boundary stays in the same place, but the stroke grows on both sides of it.
Then set `fill=None` to return to an outline-only circle.

You can now place basic shapes and choose their outline and fill. Next, overlap two shapes to learn how drawing order works.

[Previous: basic shapes](02-shapes.md) · [Next: drawing order](04-drawing-order.md)
