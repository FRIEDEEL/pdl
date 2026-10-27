"""Build a microscope bottom-up from named, adjustable polygonal assemblies.

Run: uv run python -m examples.spatial.microscope

All dimensions are schematic millimeters, not a manufacturing specification.
The example-local Assembly is a composition recipe, not a public pdl Group3D.
Round parts use polygonal faces so the entire scene supports BSP visibility.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from math import cos, pi, sin

from examples._shared import export, latin_font
from pdl import (
    Canvas,
    Color,
    DirectionalLight,
    Drawing,
    OrthographicCamera,
    Point3D,
    Polyhedron,
    Scene3D,
    Style,
    Text,
    Transform,
    Transform3D,
    Vector3D,
)

IVORY = Color(0.83, 0.86, 0.86)
DARK = Color(0.19, 0.24, 0.29)
METAL = Color(0.57, 0.65, 0.70)
BLUE = Color(0.22, 0.57, 0.70)
GLASS = Color(0.57, 0.82, 0.86)
GOLD = Color(0.91, 0.68, 0.29)
INK = Color(0.13, 0.19, 0.24)


@dataclass
class Assembly:
    """Keep named children and a local frame until the final scene is flattened.

    Edit a child through ``parts[name]``; placement changes preserve its recipe.
    Flatten exactly once, after composing the whole microscope, so visibility
    is solved across assemblies rather than separately inside each component.
    """

    parts: dict[str, Polyhedron | Assembly] = field(
        default_factory=lambda: dict[str, Polyhedron | Assembly]()
    )
    transform: Transform3D = Transform3D()

    def solids(self, parent: Transform3D = Transform3D()) -> tuple[Polyhedron, ...]:
        """Evaluate nested local transforms into world-space polygonal solids."""
        frame = parent @ self.transform
        result: list[Polyhedron] = []
        for part in self.parts.values():
            if isinstance(part, Assembly):
                result.extend(part.solids(frame))
            else:
                result.append(part.transformed(frame))
        return tuple(result)


def extrude(outline: tuple[tuple[float, float], ...], height: float, color: Color) -> Polyhedron:
    """Extrude a counterclockwise xy outline upward; concave outlines are allowed."""
    n = len(outline)
    vertices = tuple(Point3D(x, y, z) for z in (0, height) for x, y in outline)
    faces = (tuple(reversed(range(n))), tuple(range(n, 2 * n))) + tuple(
        (i, (i + 1) % n, (i + 1) % n + n, i + n) for i in range(n)
    )
    return Polyhedron(vertices, faces, color=color, stroke=None)


def block(width: float, depth: float, height: float, color: Color) -> Polyhedron:
    """Make a block centered in xy, with its bottom at z=0."""
    return extrude(
        (
            (-width / 2, -depth / 2),
            (width / 2, -depth / 2),
            (width / 2, depth / 2),
            (-width / 2, depth / 2),
        ),
        height,
        color,
    )


def barrel(
    radius: float, height: float, color: Color, *, top_radius: float | None = None, sides: int = 16
) -> Polyhedron:
    """Make a faceted cylinder or tapered barrel along local +z."""
    top = radius if top_radius is None else top_radius
    vertices = tuple(
        Point3D(r * cos(2 * pi * i / sides), r * sin(2 * pi * i / sides), z)
        for z, r in ((0, radius), (height, top))
        for i in range(sides)
    )
    faces = (tuple(reversed(range(sides))), tuple(range(sides, 2 * sides))) + tuple(
        (i, (i + 1) % sides, (i + 1) % sides + sides, i + sides) for i in range(sides)
    )
    return Polyhedron(vertices, faces, color=color, stroke=None)


def at(
    part: Polyhedron | Assembly,
    x: float = 0,
    y: float = 0,
    z: float = 0,
    *,
    rotation: Transform3D = Transform3D(),
) -> Assembly:
    """Place a reusable recipe without changing the original component."""
    return Assembly({"body": part}, Transform3D.translate(x, y, z) @ rotation)


def make_base(width: float = 64, depth: float = 72) -> Assembly:
    """Build a beveled footprint, rubber feet, and an illumination housing."""
    w, d, bevel = width / 2, depth / 2, 9
    outline = (
        (-w + bevel, -d),
        (w - bevel, -d),
        (w, -d + bevel),
        (w, d - bevel),
        (w - bevel, d),
        (-w + bevel, d),
        (-w, d - bevel),
        (-w, -d + bevel),
    )
    parts: dict[str, Polyhedron | Assembly] = {
        "housing": at(extrude(outline, 8, IVORY), z=3),
        "lamp_mount": at(barrel(11, 4, DARK), y=-10, z=11),
        "lamp_lens": at(barrel(8, 1, GLASS), y=-10, z=15),
    }
    for x in (-22, 22):
        for y in (-25, 25):
            parts[f"foot_{x}_{y}"] = at(barrel(5, 3, DARK, sides=12), x, y)
    return Assembly(parts)


def make_stand(height: float = 97) -> Assembly:
    """A swept-looking rear support, with separate coarse/fine focus wheels."""
    # Draw the arm profile in local xy, extrude it, then map xy to world yz.
    profile = (
        (13, 11),
        (29, 11),
        (29, height - 10),
        (21, height),
        (-9, height),
        (-9, height - 12),
        (13, height - 12),
    )
    to_yz = Transform3D(Vector3D(0, 1, 0), Vector3D(0, 0, 1), Vector3D(1, 0, 0))
    arm = extrude(profile, 16, IVORY).transformed(Transform3D.translate(-8, 0, 0) @ to_yz)
    parts: dict[str, Polyhedron | Assembly] = {"arm": arm}
    for side in (-1, 1):
        axis = Transform3D.rotate(90 * side, Vector3D(0, 1, 0))
        parts[f"coarse_{side}"] = at(barrel(10, 7, DARK), side * 8, 21, 48, rotation=axis)
        parts[f"fine_{side}"] = at(barrel(5, 4, METAL), side * 15, 21, 48, rotation=axis)
    return Assembly(parts)


def make_stage(width: float = 48, depth: float = 42) -> Assembly:
    """Build an aperture from four rails, then add slide, sample, and clips."""
    hole = 12
    parts: dict[str, Polyhedron | Assembly] = {
        "left": at(block((width - hole) / 2, depth, 4, DARK), -(width + hole) / 4),
        "right": at(block((width - hole) / 2, depth, 4, DARK), (width + hole) / 4),
        "front": at(block(hole, (depth - hole) / 2, 4, DARK), y=-(depth + hole) / 4),
        "back": at(block(hole, (depth - hole) / 2, 4, DARK), y=(depth + hole) / 4),
        "slide": at(block(32, 12, 0.8, GLASS), z=4),
        "sample": at(block(6, 5, 0.2, BLUE), z=4.8),
    }
    for x in (-19, 19):
        parts[f"clip_{x}"] = at(block(2, 17, 0.8, METAL), x, -3, 4.2)
    return Assembly(parts)


def make_objective(length: float = 15, band: Color = BLUE) -> Assembly:
    """An interchangeable objective, extending downward from its mounting point."""
    return Assembly(
        {
            "barrel": at(barrel(3.5, length - 3, METAL), z=-length + 3),
            "band": at(barrel(3.6, 2, band), z=-length + 5),
            "tip": at(barrel(2.2, 3, DARK, top_radius=3.5), z=-length),
            "lens": at(barrel(1.7, 0.3, GLASS), z=-length - 0.3),
        }
    )


def make_optics(tube_length: float = 23, objective_length: float = 17) -> Assembly:
    """Combine turret, three objectives, and a pair of inclined eyepieces."""
    parts: dict[str, Polyhedron | Assembly] = {
        "turret": barrel(10, 4, DARK),
        "head": at(block(25, 18, 12, IVORY), y=3, z=10),
    }
    for i, (angle, length, band) in enumerate(
        ((-90, objective_length, BLUE), (30, 12, GOLD), (150, 10, Color(0.8, 0.3, 0.3)))
    ):
        a = angle * pi / 180
        parts[f"objective_{i}"] = at(make_objective(length, band), 7 * cos(a), 7 * sin(a))
    tilt = Transform3D.rotate(24, Vector3D(1, 0, 0))
    for x in (-7, 7):
        tube = Assembly(
            {
                "tube": barrel(4.5, tube_length, METAL),
                "eyecup": at(barrel(5.5, 6, DARK), z=tube_length),
                "glass": at(barrel(3.8, 0.4, GLASS), z=tube_length + 6),
            }
        )
        parts[f"eyepiece_{x}"] = at(tube, x, 3, 22, rotation=tilt)
    return Assembly(parts)


def make_microscope(
    stage_height: float = 48,
    tube_length: float = 23,
    objective_length: float = 17,
    exploded: bool = False,
) -> Assembly:
    """Compose the microscope in the same order as its physical decomposition.

    stage_height adjusts the stage and condenser together. The optics remain
    fixed on the stand. Exploded offsets are illustrative assembly separation.
    """
    base = make_base()
    stand = make_stand()
    stage = make_stage()
    illumination = Assembly(
        {
            "condenser": barrel(6, 7, DARK, top_radius=9),
            "iris_ring": at(barrel(8, 2, METAL), z=-2),
        }
    )
    optics = make_optics(tube_length, objective_length)
    # These are the editable assembly placements; all subparts remain named.
    return Assembly(
        {
            "base": base,
            "stand": at(stand, y=26 if exploded else 0),
            "stage": at(stage, y=-40 if exploded else -10, z=stage_height),
            "illumination": at(illumination, y=-10, z=stage_height - 15),
            "optics": at(optics, z=106 if exploded else 78, y=-10),
        }
    )


def example() -> Canvas:
    """Show the complete instrument and the same named recipes separated."""
    canvas = Canvas(290, 205)
    font = latin_font()

    def label(text: str, x: float, y: float, size: float = 10) -> None:
        canvas.draw(Text(text, font=font, size=size, position=(x, y)), Style(stroke=None, fill=INK))

    label("A microscope, built from components", 12, 190, 20)
    label("Named Python assemblies / polygonal surfaces / BSP visibility", 12, 180)
    camera = OrthographicCamera(azimuth=-55, elevation=23)
    light = DirectionalLight(Vector3D(-1, 1, -3), ambient=0.45)
    for x, exploded in ((75, False), (215, True)):
        instrument = make_microscope(exploded=exploded)
        scene = Scene3D(instrument.solids(), camera=camera, light=light, visibility="bsp")
        projected = scene.project()
        assert projected.visibility == "bsp"
        canvas.draw(Drawing(projected, transform=Transform.translate(x, 38)))
    label("ASSEMBLED", 44, 20, 11)
    label("COMPONENT STUDY", 180, 20, 11)
    label("Base / stand + focus / stage + slide / condenser / optics", 12, 8, 9)
    return canvas


if __name__ == "__main__":
    export(example(), __file__, tikz_mode="pdf")
