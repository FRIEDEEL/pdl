"""Build a microscope bottom-up from named, adjustable polygonal assemblies.

Run: uv run python -m examples.spatial.microscope

All dimensions are schematic millimeters, not a manufacturing specification.
The example-local Assembly is a composition recipe, not a public pdl Group3D.
Round parts use polygonal faces so the entire scene supports BSP visibility.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from math import cos, pi, sin

from examples._shared import export, latin_font, output_base
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
    parts["switch_plate"] = at(block(12, 7, 0.6, DARK), 17, -22, 11)
    parts["power_switch"] = at(block(4, 4, 1.5, METAL), 14, -22, 11.6)
    parts["power_indicator"] = at(barrel(0.9, 0.3, BLUE, sides=12), 20, -22, 11.6)
    parts["brightness"] = at(barrel(3, 2, DARK), -20, -22, 11)
    for x in (-22, 22):
        for y in (-25, 25):
            parts[f"foot_{x}_{y}"] = at(barrel(5, 3, DARK, sides=12), x, y)
    return Assembly(parts)


def gear(radius: float = 5.5, thickness: float = 3, teeth: int = 14) -> Polyhedron:
    """Extrude a schematic tooth profile, not an involute engineering gear."""
    outline = tuple(
        (r * cos(2 * pi * (i + phase) / teeth), r * sin(2 * pi * (i + phase) / teeth))
        for i in range(teeth)
        for phase, r in ((0, radius - 1), (0.22, radius), (0.55, radius), (0.78, radius - 1))
    )
    return extrude(outline, thickness, GOLD)


def make_screw(radius: float = 1.1) -> Assembly:
    """A shallow screw head with a contrasting straight driver slot."""
    return Assembly(
        {
            "head": barrel(radius, 0.6, METAL, sides=12),
            "slot": at(block(radius * 1.4, 0.25, 0.08, DARK), z=0.6),
        }
    )


def make_focus_wheel(radius: float = 9, width: float = 5) -> Assembly:
    """Build a knurled handwheel, inset face, hub, and retaining screw."""
    parts: dict[str, Polyhedron | Assembly] = {
        "rim": barrel(radius, width, DARK, sides=24),
        "face": at(barrel(radius - 1, 0.6, METAL, sides=24), z=width),
        "hub": at(barrel(radius * 0.38, 1.2, DARK), z=width + 0.6),
        "retainer": at(make_screw(), z=width + 1.8),
    }
    for i in range(24):
        angle = i * 2 * pi / 24
        parts[f"grip_{i:02}"] = at(
            block(0.65, 0.7, width - 0.6, METAL),
            (radius - 0.1) * cos(angle),
            (radius - 0.1) * sin(angle),
            0.3,
            rotation=Transform3D.rotate(i * 15),
        )
    return Assembly(parts)


def make_focus_drive(stage_height: float = 48, *, open_drive: bool = False) -> Assembly:
    """Connect a fixed transverse shaft to a moving rack and stage saddle.

    Tooth shapes and the fine-focus coupling are illustrative, not a simulated
    transmission. Changing stage_height translates the rack/saddle together;
    the pinion rotates by the corresponding nominal pitch-radius travel.
    """
    travel = stage_height - 48
    shaft_axis = Transform3D.rotate(90, Vector3D(0, 1, 0))
    front_axis = Transform3D.rotate(90, Vector3D(1, 0, 0))
    parts: dict[str, Polyhedron | Assembly] = {
        "shaft": at(barrel(2, 38, METAL), -19, 4, 48, rotation=shaft_axis),
        "pinion": at(
            gear(), 10, 4, 48, rotation=shaft_axis @ Transform3D.rotate(-travel / 4.8 * 180 / pi)
        ),
        "rack_spine": at(block(3, 2, 43, GOLD), 11.5, 10.1, 27 + travel),
        "saddle": at(block(17, 3, 19, BLUE), y=7, z=stage_height - 10),
    }
    for i in range(25):
        parts[f"rack_tooth_{i:02}"] = at(
            block(3, 1.2, 0.85, GOLD), 11.5, 8.5, 27.4 + 1.55 * i + travel
        )
    for x in (-7, 7):
        parts[f"guide_{x}"] = at(block(2.5, 3, 54, METAL), x, 11, 22)
        parts[f"slide_shoe_{x}"] = at(block(4, 4, 18, DARK), x, 9, stage_height - 9)
        # Two side brackets leave the illumination axis open under the stage.
        parts[f"stage_bracket_{x}"] = at(block(4, 19, 5, METAL), x, -2, stage_height - 5)
        parts[f"saddle_screw_{x}"] = at(make_screw(), x, 4.8, stage_height + 5, rotation=front_axis)
    for side in (-1, 1):
        axis = Transform3D.rotate(side * 90, Vector3D(0, 1, 0))
        parts[f"bearing_{side}"] = at(barrel(4.2, 5, METAL), side * 12, 4, 48, rotation=axis)
        if not open_drive or side == -1:
            parts[f"coarse_{side}"] = at(make_focus_wheel(), side * 18, 4, 48, rotation=axis)
            parts[f"fine_{side}"] = at(make_focus_wheel(4.2, 3), side * 27, 4, 48, rotation=axis)
    return Assembly(parts)


def make_stand(height: float = 97) -> Assembly:
    """Build the cast support with a recessed back strip and mounting hardware."""
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
    parts: dict[str, Polyhedron | Assembly] = {
        "casting": arm,
        "rear_inset": at(block(9, 0.8, 52, METAL), y=29.2, z=25),
        "head_mount": at(barrel(8, 4, METAL), y=-6, z=83),
    }
    for x in (-5, 5):
        parts[f"base_bolt_{x}"] = at(make_screw(1.5), x, 22, 11)
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
        parts[f"clip_{x}"] = Assembly(
            {
                "leaf": at(block(2, 17, 0.65, METAL), x, -3, 4.2),
                "pivot": at(make_screw(1.4), x, 4, 4.8),
                "toe": at(block(3, 3, 0.6, METAL), x, -10, 4.7),
            }
        )
    parts["front_trim"] = at(block(width - 4, 1, 1, METAL), y=-depth / 2, z=1)
    axis = Transform3D.rotate(90, Vector3D(0, 1, 0))
    parts["stage_control"] = at(make_focus_wheel(3.2, 3), width / 2, 10, -2, rotation=axis)
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
    focus_drive = make_focus_drive(stage_height)
    # These are the editable assembly placements; all subparts remain named.
    return Assembly(
        {
            "base": base,
            "stand": at(stand, y=26 if exploded else 0),
            "focus_drive": focus_drive,
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


def focus_detail() -> Canvas:
    """Compare the earlier block/knob sketch with an exposed drive assembly."""
    canvas = Canvas(230, 130)
    font = latin_font()
    camera = OrthographicCamera(azimuth=-52, elevation=18, target=Point3D(0, 5, 48))
    old = Assembly({"stand": at(block(16, 16, 50, IVORY), y=21, z=23)})
    for side in (-1, 1):
        axis = Transform3D.rotate(side * 90, Vector3D(0, 1, 0))
        old.parts[f"knob_{side}"] = at(barrel(10, 7, DARK), side * 8, 21, 48, rotation=axis)
    old.parts["stage"] = at(make_stage(), y=-10, z=48)
    # Opaque pale colors avoid obscuring the reference with back-face transparency.
    pale = tuple(replace(p, color=Color(0.85, 0.87, 0.89)) for p in old.solids())
    detailed = make_focus_drive(open_drive=True)
    scenes = (pale, detailed.solids())
    for x, solids in zip((57, 163), scenes, strict=True):
        scene = Scene3D(
            solids,
            camera=camera,
            visibility="bsp",
            light=DirectionalLight(Vector3D(-1, 1, -3), ambient=0.7 if x == 57 else 0.45),
        ).project()
        canvas.draw(
            Drawing(
                scene,
                transform=Transform.translate(x, 58) @ Transform.scale(1.1 if x == 57 else 1.25),
            )
        )
    for text, x, y, size in (
        ("Focus mechanism / component detail", 10, 116, 17),
        ("Earlier simplified support", 10, 16, 10),
        ("Rack, pinion, guides and saddle", 119, 16, 10),
        ("Near-side handwheel removed to expose the drive", 119, 8, 7),
    ):
        canvas.draw(Text(text, font=font, size=size, position=(x, y)), Style(stroke=None, fill=INK))
    return canvas


if __name__ == "__main__":
    export(example(), __file__, tikz_mode="pdf")
    detail = focus_detail()
    base = output_base(__file__).with_name("microscope-focus")
    detail.save(base.with_suffix(".svg"), backend="svg")
    detail.save(base.with_suffix(".tex"), backend="tikz", tikz_mode="pdf")
