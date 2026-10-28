# Placement, groups, and references

Concrete shapes, text, groups and reference objects inherit Entity and expose
mutable authoring operations directly. Drawing describes independent
placement. Group owns a single-parent local structure; Gather is a flat operation
set that may cross layers. References and draws capture state before later edits.

## Entity

```{eval-rst}
.. autoclass:: pdl.Entity
   :exclude-members: description_only, automatic_layer, placement, assigned_layer, local_snapshot, to_path
   :members:
   :undoc-members:
   :member-order: bysource
```

## Drawing

```{eval-rst}
.. autoclass:: pdl.Drawing
   :members:
   :undoc-members:
   :member-order: bysource
```

## Group

```{eval-rst}
.. autoclass:: pdl.Group
   :members:
   :undoc-members:
   :member-order: bysource
```

## Connection

```{eval-rst}
.. autoclass:: pdl.Connection
   :members:
   :undoc-members:
   :member-order: bysource
```

## Node

```{eval-rst}
.. autoclass:: pdl.Node
   :members:
   :undoc-members:
   :member-order: bysource
```

## bounds

```{eval-rst}
.. autofunction:: pdl.bounds
```

## Gather

```{eval-rst}
.. autoclass:: pdl.Gather
   :members:
   :member-order: bysource
```


## Frame

```{eval-rst}
.. autoclass:: pdl.Frame
   :members:
   :member-order: bysource
```

## ReferencePoint

```{eval-rst}
.. autoclass:: pdl.ReferencePoint
   :members:
   :member-order: bysource
```
