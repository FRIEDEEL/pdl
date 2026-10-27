# 20. Fill with gradients and opacity

A gradient replaces the solid Color in Style.fill. Start with color stops,
then choose a linear direction or a radial center and radius.

```{literalinclude} ../../../examples/tutorial/paint/gradients.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![20. Fill with gradients and opacity](../../../examples/output/tutorial/paint/gradients.svg)

[Complete runnable example](../../../examples/tutorial/paint/gradients.py)

Offsets must strictly increase from zero to one. The pale stop at 0.4 moves
the bright band away from the middle. LinearGradient defaults left-to-right;
the square explicitly uses the lower-left to upper-right diagonal.

Coordinates are normalized in each leaf shape's local geometry bounds:
(0, 0) is lower-left and (1, 1) is upper-right. The upper bar shows the same
local gradient after rotation. A shared Group fill is evaluated independently
for each leaf, not across the combined Group bounds.

RadialGradient defaults to center (0.5, 0.5), radius 0.5. Non-square bounds
produce an ellipse. Outside the endpoint/radius, colors stay at the nearest
end stop. Only opaque RGB stops, pad spreading, and fill gradients are
supported; native Text/TeX still require solid colors. SVG uses native gradient
resources; TikZ emits PDF functional shadings, which require a compatible PDF
viewer/print pipeline. See the [PGF shading manual](https://tikz.dev/base-shadings).

Try changing the middle offset, reversing the linear direction, or moving the
radial center to (0.3, 0.7).

## Per-object opacity

Gather.set_opacity applies a command to selected targets. These two circles
overlap at 75% combined opacity, although each is 50% opaque. This is not
isolated group compositing. Explicit child styles retain their precedence.

```{literalinclude} ../../../examples/tutorial/paint/opacity.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![Opacity](../../../examples/output/tutorial/paint/opacity.svg)

[Source](../../../examples/tutorial/paint/opacity.py)
