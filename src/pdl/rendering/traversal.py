"""Backend capability dispatch before recursive composite lowering."""

from collections.abc import Callable, Iterator

from pdl.geometry.transforms import Transform
from pdl.scene.composition import Composite, Drawing
from pdl.scene.evaluation import layout_session
from pdl.scene.paint import Style


def prepare(
    drawings: tuple[Drawing, ...],
    supports: Callable[[Drawing], bool],
    transform: Transform = Transform(),
    style: Style | None = None,
    ancestors: frozenset[int] = frozenset(),
) -> Iterator[Drawing]:
    """Keep supported objects intact, otherwise apply their authoring rules.

    Traversal follows paint order. Dependency evaluation may inspect another
    object first, but neither inserts it into this sequence nor changes order.
    """
    with layout_session() as context:
        for drawing in drawings:
            placed = Drawing(
                drawing.geometry,
                drawing.style if drawing.style is not None else style,
                transform @ drawing.transform,
            )
            geometry = drawing.geometry
            if supports(placed) or not isinstance(geometry, Composite):
                yield placed
                continue
            if id(geometry) in ancestors:
                raise ValueError(f"Cyclic composite graph: {type(geometry).__name__}.")
            yield from prepare(
                context.decompose(geometry),
                supports,
                placed.transform,
                placed.style,
                ancestors | {id(geometry)},
            )
