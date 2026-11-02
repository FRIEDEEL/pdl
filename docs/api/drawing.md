# Canvas and paint

Canvas owns submission capture, layer order, viewport policy, and save/render
entrypoints. It accepts Entities and expandable extension components. Supply a
Style on the Entity or a per-submission override; explicit Group member styles
retain priority. Captured records keep the effective values used at submission.

Style is an immutable complete value. None disables a stroke/fill inside Style;
Entity.style None requests inheritance/default resolution. Gradients use initial
normalized bounds and current numerical frames after transformation.

## Canvas

```{eval-rst}
.. autoclass:: pdl.Canvas
   :members:
   :member-order: bysource
```

## Viewport and adapter contract

Viewport contains current output Entities, page dimensions in millimeters, and
the effective world-to-page output_transform. Backends depend on the narrower
Page protocol rather than the Canvas implementation.

```{eval-rst}
.. autoclass:: pdl.canvas.records.Viewport
   :members:

.. autoclass:: pdl.canvas.records.Page
   :members:
```

## Color

```{eval-rst}
.. autoclass:: pdl.Color
   :members:
   :member-order: bysource
```

## Style

```{eval-rst}
.. autoclass:: pdl.Style
   :members:
   :member-order: bysource
```

## Layer

```{eval-rst}
.. autoclass:: pdl.Layer
   :members:
   :member-order: bysource
```

## LayerStack

```{eval-rst}
.. autoclass:: pdl.LayerStack
   :members:
   :member-order: bysource
```

## ColorStop

```{eval-rst}
.. autoclass:: pdl.ColorStop
   :members:
   :member-order: bysource
```

## LinearGradient

```{eval-rst}
.. autoclass:: pdl.LinearGradient
   :members:
   :member-order: bysource
```

## RadialGradient

```{eval-rst}
.. autoclass:: pdl.RadialGradient
   :members:
   :member-order: bysource
```

## image drawing factory

```{eval-rst}
.. autofunction:: pdl.image
```

Image stores captured PNG/JPEG bytes and current viewport corners. See the [image lesson](../tutorial/en/04-finish/02-images.md).
