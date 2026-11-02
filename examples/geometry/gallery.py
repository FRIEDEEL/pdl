"""Basic geometry and painted paths through both backends.

Run with ``uv run python -m examples.geometry.gallery``.
"""

from examples._shared import export
from pdl import Canvas, Color, Style, circle, line, polygon, polyline, rectangle
from pdl.author.entity.factories import as_entity
from pdl.author.geometry import Path as PathGeometry
from pdl.author.geometry.shapes import Arc as ArcGeometry
from pdl.author.geometry.shapes import Rectangle as RectangleGeometry


def gallery() -> Canvas:
    blue = Color(0.15, 0.4, 0.8)
    pale = Color(0.8, 0.9, 1)
    paint = Style(stroke=blue, fill=pale, line_width=0.6)
    line_entity = line((5, 80), (30, 80))
    polyline_entity = polyline(((40, 75), (50, 85), (65, 75)))
    circle_entity = circle((85, 80), 7)
    rectangle_entity = rectangle((5, 50), 25, 15)
    polygon_entity = polygon(((40, 50), (55, 65), (65, 50)))
    angle_arc = ArcGeometry.from_tikz((78, 55), radius=8, start_angle=180, end_angle=450)
    endpoint_arc = ArcGeometry.from_svg(
        (100, 50), (115, 65), radius_x=12, radius_y=6, rotation=25, sweep=True
    )
    curve = (
        PathGeometry()
        .move_to((5, 30))
        .quadratic_to((20, 48), (35, 30))
        .cubic_to((45, 10), (55, 50), (65, 30))
    )
    ring = (
        RectangleGeometry((80, 10), 30, 25)
        .to_path()
        .move_to((87, 17))
        .line_to((103, 17))
        .line_to((103, 28))
        .line_to((87, 28))
        .close()
    )
    background = rectangle((5, 5), 20, 10)
    foreground = circle((23, 12), 6)
    canvas = Canvas(120, 90)
    canvas.draw(line_entity, Style(line_width=0.8, line_cap="round"))
    canvas.draw(polyline_entity, Style(stroke=blue))
    for geometry in (circle_entity, rectangle_entity, polygon_entity, angle_arc, endpoint_arc):
        canvas.draw(as_entity(geometry), paint)
    canvas.draw(as_entity(curve), Style(stroke=blue, line_width=0.8))
    canvas.draw(as_entity(ring), Style(fill=pale, stroke=blue, fill_rule="evenodd"))
    canvas.draw(background, paint)
    canvas.draw(foreground, Style(fill=Color(1, 0.6, 0.2), stroke=None))
    return canvas


if __name__ == "__main__":
    export(gallery(), __file__)
