# 1.2 Draw some shapes

In the first chapter, `Node` provided a ready-made box around text.
Now we will draw shapes directly, without any text inside them.

## A triangle, a rectangle, and a circle

```{literalinclude} ../../../../examples/tutorial/basics/shapes.py
:language: python
:start-at: from pdl import
:end-before: output =
```

![shapes](../../../../examples/output/tutorial/basics/shapes.svg)

[Source file](../../../../examples/tutorial/basics/shapes.py)

The three shapes have black outlines and no fill. That is the default when
you draw these shapes without supplying a style.

`Polygon` connects the supplied points in order and closes the outline back
to the first point. Here the triangle has a horizontal base from `(10, 10)`
to `(30, 10)` and a top vertex at `(20, 30)`. Add more vertices to make other
polygons.

`Rectangle((40, 10), width=25, height=20)` starts at its **lower-left corner**,
then extends 25 mm to the right and 20 mm upward. Its upper-right corner is
therefore `(65, 30)`.

`Circle((85, 20), radius=10)` uses a **center and radius**. The circle extends
from x = 75 to x = 95 and from y = 10 to y = 30.

Notice that the position argument has a different meaning for each object:
a Node uses its center, a Rectangle uses its lower-left corner, and a Circle
uses its center. A Polygon uses the vertices you supply.

## See where a coordinate lands

Let's put just one circle on a smaller canvas. The light gray lines below
connect its center to the x and y axes. The label `(20, 15)` means 20 mm right
and 15 mm up from the origin, not from the edge of the circle.

```{literalinclude} ../../../../examples/tutorial/basics/coordinates.py
:language: python
:start-at: from pdl import
:end-before: output =
```

![coordinates](../../../../examples/output/tutorial/basics/coordinates.svg)

[Source file](../../../../examples/tutorial/basics/coordinates.py)

The code after `# Optional guides` only draws the axes, guide lines, and
labels. Those marks are ordinary drawing objects, not an automatic coordinate
overlay. You can remove that entire section and the circle stays in the same
place. The axes lie along the canvas edges, so half of each axis stroke is
clipped at the boundary.

`Line` draws a segment between two points. `Text` supplies the labels. We will
cover text and style options in more detail later; you do not need to reproduce
the guides in every drawing.

## Try a small change

In the first script, change the rectangle's width from `25` to `15`.
Its left edge stays at x = 40; only its right edge moves.
Then change the circle's radius from `10` to `6`. Its center stays at `(85, 20)`.

In the coordinate example, change the circle's center to `(20, 22)`.
It moves upward. The guides are drawn separately, so they still point to the
old center until you edit their coordinates too.


---

[Part contents](index.md)
