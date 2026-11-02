"""Perspective polygon visibility: same source faces, centroid versus BSP.

Run: uv run python -m examples.spatial.visibility
"""

from dataclasses import replace

from examples._shared import export, latin_font
from pdl import Canvas, Color, Style, text
from pdl.author.entity.factories import as_entity
from pdl.author.transform import Scaling, Translation
from pdl.extensions.spatial import PerspectiveCamera, Point3D, Polyhedron, Scene3D

CAMERA = PerspectiveCamera(0, 0, distance=240, focal_length=240)
BLUE = Color(0.15, 0.57, 0.78)
ORANGE = Color(0.9, 0.35, 0.24)
GREEN = Color(0.44, 0.7, 0.3)


def world(x: float, y: float, depth: float) -> Point3D:
    """Map camera-plane coordinates and axial distance to a world point."""
    return Point3D(240 - depth, x, y)


def panel(vertices: tuple[Point3D, ...], color: Color) -> Polyhedron:
    """A single two-sided face; a Polyhedron need not be a closed shell."""
    return Polyhedron(vertices, (tuple(range(len(vertices))),), color=color, line_width=0.25)


def parallel_panels() -> tuple[Polyhedron, ...]:
    """A smaller rear face is incorrectly put in front by global center sorting."""
    foreground = panel(
        tuple(world(x, y, 210 + 0.6 * x) for x, y in ((-45, -25), (60, -25), (60, 25), (-45, 25))),
        BLUE,
    )
    background = panel(
        tuple(
            world(x, y, 218 + 0.6 * x) for x, y in ((-42, -20), (-15, -20), (-15, 20), (-42, 20))
        ),
        ORANGE,
    )
    return foreground, background


def crossed_panels() -> tuple[Polyhedron, ...]:
    """Two planes exchange front/back relation across their intersection."""
    return tuple(
        panel(
            tuple(
                world(x, y, 240 + slope * x)
                for x, y in ((-45, -32), (45, -32), (45, 32), (-45, 32))
            ),
            color,
        )
        for slope, color in ((0.7, ORANGE), (-0.7, BLUE))
    )


def cyclic_ribbons() -> tuple[Polyhedron, ...]:
    """Three disjoint ribbons have no valid whole-face painter permutation."""
    corners = ((-42.0, -25.0), (42.0, -25.0), (0.0, 44.0))
    ribbons: list[Polyhedron] = []
    for i, color in enumerate((ORANGE, BLUE, GREEN)):
        a, b = corners[i], corners[(i + 1) % 3]
        dx, dy = b[0] - a[0], b[1] - a[1]
        length = (dx * dx + dy * dy) ** 0.5
        vertices: list[Point3D] = []
        for t, offset in ((-0.08, -8), (1.08, -8), (1.08, 8), (-0.08, 8)):
            x, y = a[0] + t * dx - offset * dy / length, a[1] + t * dy + offset * dx / length
            depth = 1 / ((1 - t) / 210 + t / 260)
            vertices.append(world(x * depth / 240, y * depth / 240, depth))
        ribbons.append(panel(tuple(vertices), color))
    return tuple(ribbons)


def example() -> Canvas:
    """Keep the exact same geometry and color in both reference and BSP columns."""
    canvas = Canvas(310, 425)
    font = latin_font()
    ink = Style(stroke=None, fill=Color(0.12, 0.18, 0.25))

    def label(value: str, x: float, y: float, size: float = 10) -> None:
        canvas.draw(text(value, font=font, position=(x, y), size=size), ink)

    label("Polygon visibility / perspective", 12, 408, 23)
    label("Centroid reference", 20, 395)
    label("BSP visibility", 175, 395)
    cases = (
        ("Parallel faces", parallel_panels()),
        ("Intersecting faces", crossed_panels()),
        ("Cyclic occlusion", cyclic_ribbons()),
        ("Transparent intersections", tuple(replace(p, opacity=0.5) for p in crossed_panels())),
    )
    for row, (title, objects) in enumerate(cases):
        y = 303 - row * 96
        label(title, 12, y + 74)
        scene = Scene3D(objects, CAMERA, light=None, visibility="centroid")
        before = scene.project()
        after = replace(scene, visibility="bsp").project()
        for x, view in ((78, before), (233, after)):
            canvas.draw(as_entity(view, transform=Translation(x, y + 35) @ Scaling(0.65)))
        label(f"{len(before.children)} whole faces", 20, y, 8)
        label(f"{len(after.children)} fragments / original edges only", 175, y, 8)
    return canvas


if __name__ == "__main__":
    export(example(), __file__, tikz_mode="pdf")
