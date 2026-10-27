# Group, Layer, and Gather: structure, order, and selection

These three mechanisms answer different questions. Group defines a spatial
assembly, Layer defines coverage order, and Gather selects existing units for
commands. They are not interchangeable kinds of containers.

| | Group | Layer | Gather |
|---|---|---|---|
| Purpose | Local structure and shared placement | Bottom-to-top coverage | Shared imperative operations |
| One instance may belong to | One direct parent Group | One effective layer for its outermost unit | Multiple Gathers |
| Spatial transform | Transforms the assembly | None | Applies a command to every selected unit |
| Retained relationship | Local coordinates and inherited defaults | Coverage order | Membership only, not spatial constraints |
| Nesting | Yes | No layer groups in this stage | Flat; adding a Gather copies its members |
| Draw directly | Yes | No | No |

## Shared members are the defining feature of Gather

Consider `g1 = Gather(a, b)` and `g2 = Gather(b, c)`. Both reference the same B.
Neither selection owns it, and adding it to the second selection creates no copy.

```{literalinclude} ../../../examples/tutorial/layout/shared_gathers.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![Two overlapping Gathers change one another's relative arrangement](../../../examples/output/tutorial/layout/shared_gathers.svg)

[Complete runnable source](../../../examples/tutorial/layout/shared_gathers.py)

Gray circles mark the original positions in both panels. The top panel executes
only the first command. The bottom starts from the same initial state and
executes both commands in order:

1. Moving g1 up moves A and B. C stays put, so the B-to-C arrangement inside g2
   changes even though no command has been issued to g2 yet.
2. Moving g2 right moves B and C. A stays put, so the A-to-B arrangement inside
   g1 changes. B has received both commands, each exactly once.

**Gather preserves membership, not a local coordinate relationship.** It stores
no parent transformation or constraint that would move the other members when
one shared member changes through another selection.

This does not mean a Gather transform randomly distorts its members. A single
command applies the same world-space affine transformation to all its current
targets: translation preserves their spacing, while rotation or scaling acts
about the common specified pivot. The relationship is not protected against
subsequent operations through other overlapping selections.

Within one command, duplicate targets are processed once. Across two commands,
a shared target receives both, in call order. Nested Gather membership never
persists: `Gather(g1, g2)` makes a flat union of the current identities.

## Group keeps an assembly's local structure

A Group retains a local coordinate structure, so transforming the Group moves
all its parts through the same parent placement. A Group can itself be a part
of another Group, but each instance has only one direct parent.

Gather selections treat the outermost Group as one operation unit. Attempting
to select an internal part promotes the target to that outermost Group with a
warning. This prevents an overlapping Gather from accidentally moving only one
part of an assembly.

Group is not an immutable or rigid-body constraint: explicitly editing,
adding, or removing its members can still change the internal arrangement.
The guarantee is that operating on the Group preserves its members' local
placements, not that every possible edit preserves distances.

## Layer stays independent of spatial selection

A Layer has no geometric transform. Its members may be independent instances
or complete Groups, and a Gather can select units across several layers.
The whole outermost Group occupies one layer.

The [sandwich example](18-layers.md#the-sandwich-case) shows why this matters:
Gather can move a base and lid together while an unrelated object remains
between their layers. Turning the two plates into one Group raises the whole
assembly to the highest member layer, eliminating the external interleaving.

Use `layer.to_gather()` to capture its current top-level members for a command.
This does not make the layer transformable or keep the selection synchronized
with later layer membership changes.

## Choosing the right mechanism

- A symbol whose body, ports, and labels should remain an assembly: Group.
- Several independently organized objects to move or restyle now: Gather.
- Different overlapping selections of the same live instances: multiple Gathers.
- Control over what covers what: Layer.

Object edits affect subsequent draw captures; existing Canvas records do not
follow later Group or Gather operations. Reordering Layer identities does
change the coverage order of records assigned to those layers.

Try moving only g2 first, then g1. For translations the final positions are the
same, but the intermediate state differs. Replace one translation with a
rotation about the origin to see why general transform order matters.

[Previous: Layers](18-layers.md) · [Next: Images](19-images.md)
