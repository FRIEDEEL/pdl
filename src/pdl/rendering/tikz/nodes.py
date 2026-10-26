"""Native TikZ node shapes with authoring-defined sizes and label placement."""

from math import isclose

from pdl.components.nodes import Node
from pdl.rendering.formatting import number
from pdl.rendering.tikz.geometry import coordinate, paint_options
from pdl.rendering.tikz.text import render_tex, render_text
from pdl.scene.composition import Drawing
from pdl.typography.plain import Font, Text


def supports(drawing: Drawing) -> bool:
    """Use a native node when placement preserves lengths and orientation.

    Scaling, reflection and shear use general lowering, preserving fixed
    stroke widths and transformed label geometry under the existing contract.
    """
    if not isinstance(drawing.geometry, Node):
        return False
    t = drawing.transform
    return (
        isclose(t.a * t.a + t.b * t.b, 1, abs_tol=1e-12)
        and isclose(t.c * t.c + t.d * t.d, 1, abs_tol=1e-12)
        and isclose(t.a * t.c + t.b * t.d, 0, abs_tol=1e-12)
        and isclose(t.a * t.d - t.b * t.c, 1, abs_tol=1e-12)
    )


def render_node(node: Node, drawing: Drawing, commands: dict[Font, str]) -> str:
    box = node.bounds
    options = [
        node.shape,
        "anchor=center",
        "inner sep=0pt",
        "outer sep=0pt",
        f"minimum width={number(box.width)}mm",
        f"minimum height={number(box.height)}mm",
        *paint_options(node.style),
    ]
    a, b, c, d, e, f = (number(v) for v in drawing.transform.values)
    lines = [
        f"\\begin{{scope}}[cm={{{a},{b},{c},{d},({e},{f})}},transform shape]",
        "\\node[" + ",".join(options) + "] at " + coordinate(box.anchor()) + " {};",
        r"\end{scope}",
    ]
    label = node.label_drawing()
    placed = Drawing(label.geometry, label.style, drawing.transform @ label.transform)
    if isinstance(node.label, Text):
        lines.append(render_text(node.label, placed, commands))
    else:
        lines.append(render_tex(node.label, placed))
    return "\n".join(lines)
