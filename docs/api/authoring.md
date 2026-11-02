# Entities, composition, and positioning

Entity directly holds its supplied geometry. Direct edits to an explicitly
shared mutable description are shared; transformations replace only the target's
held geometry. Copy creates independent geometry and members. There is no retained
placement matrix, implicit object frame, or live anchor binding.

Style resolution reads explicit member paint, then the closest explicitly styled
Group, then the object's default. None is preserved on authoring instances.
`Entity.geometry_defaults` configures defaults for generic factory roles;
subclasses may provide their own class default. Canvas captures effective paint.

Group.set_style changes the Group alone. Gather.set_style changes exactly the
selected identities; select `*group.members` to update members explicitly.

## Entity

```{eval-rst}
.. autoclass:: pdl.Entity
   :members:
   :member-order: bysource
   :exclude-members: prepare_transform, commit_transform, bind_layer, automatic_layer
```

## Group

```{eval-rst}
.. autoclass:: pdl.Group
   :members:
   :member-order: bysource
```

## Gather

```{eval-rst}
.. autoclass:: pdl.Gather
   :members:
   :member-order: bysource
```

## Connection

```{eval-rst}
.. autoclass:: pdl.Connection
   :members:
   :member-order: bysource
```

## Node

```{eval-rst}
.. autoclass:: pdl.Node
   :members:
   :member-order: bysource
```

## Explicit construction

```{eval-rst}
.. autofunction:: pdl.author.entity.factories.as_entity
```

This helper creates an Entity from a description or an independent copy from an existing Entity, applying an optional affine map immediately.
