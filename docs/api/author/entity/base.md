# pdl.author.entity.base

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

Source: `src/pdl/author/entity/base.py`.

```{eval-rst}
.. automodule:: pdl.author.entity.base
   :members: Entity, TransformEdit, LayerRegistration
   :undoc-members:
   :ignore-module-all:
   :member-order: bysource
```
