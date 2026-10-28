# 1.4 Which object is in front?

Two objects can occupy the same part of a picture. Let's overlap an orange
rectangle and a blue circle to see what determines which one is visible.

## Draw the circle first

```{literalinclude} ../../../../examples/tutorial/layout/circle_first.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![Rectangle painted after the circle](../../../../examples/output/tutorial/layout/circle_first.svg)

[Complete runnable example](../../../../examples/tutorial/layout/circle_first.py)

The rectangle covers the right-hand part of the circle. The circle still
exists in full; the rectangle's fill simply paints over it.

## Swap the two draw calls

Keep the same shapes, coordinates, and styles. Change only the order of the
last two lines:

```{literalinclude} ../../../../examples/tutorial/layout/rectangle_first.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![Circle painted after the rectangle](../../../../examples/output/tutorial/layout/rectangle_first.svg)

[Complete runnable example](../../../../examples/tutorial/layout/rectangle_first.py)

Now the circle is in front. **Later draw calls paint above earlier ones.**
The order in which you create Python variables does not determine this order.

This also explains why `fill=None` differs from a white fill. With no fill,
the interior paints nothing, so earlier objects can show through. White fill
covers earlier objects with white.

## Try it

In the first example, set the rectangle's style to `fill=None`. Its outline
remains in front, but the blue circle shows through its interior. We have not
introduced a Layer API: these examples use the canvas's existing paint order.

API: {py:meth}`pdl.Canvas.draw`, {py:class}`pdl.Style`.


---

[Part contents](index.md)
