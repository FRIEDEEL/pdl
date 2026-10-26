"""Generate the same geometry gallery through both backends.

Run with ``uv run python examples/gallery.py`` from the repository root.
"""

from pathlib import Path as FilePath

from pdl import (
    Arc,
    Canvas,
    Circle,
    Color,
    Line,
    Path,
    Polygon,
    Polyline,
    Rectangle,
    Style,
)


def gallery() -> Canvas:
    canvas = Canvas(120, 90)
    blue = Color(0.15, 0.4, 0.8)
    pale = Color(0.8, 0.9, 1)
    paint = Style(stroke=blue, fill=pale, line_width=0.6)
    canvas.draw(Line((5, 80), (30, 80)), Style(line_width=0.8, line_cap="round"))
    canvas.draw(Polyline(((40, 75), (50, 85), (65, 75))), Style(stroke=blue))
    canvas.draw(Circle((85, 80), 7), paint)
    canvas.draw(Rectangle((5, 50), 25, 15), paint)
    canvas.draw(Polygon(((40, 50), (55, 65), (65, 50))), paint)
    canvas.draw(Arc.from_tikz((78, 55), radius=8, start_angle=180, end_angle=450), paint)
    canvas.draw(
        Arc.from_svg((100, 50), (115, 65), radius_x=12, radius_y=6, rotation=25, sweep=True),
        paint,
    )
    curve = (
        Path()
        .move_to((5, 30))
        .quadratic_to((20, 48), (35, 30))
        .cubic_to((45, 10), (55, 50), (65, 30))
    )
    canvas.draw(curve, Style(stroke=blue, line_width=0.8))
    ring = (
        Rectangle((80, 10), 30, 25)
        .to_path()
        .move_to((87, 17))
        .line_to((103, 17))
        .line_to((103, 28))
        .line_to((87, 28))
        .close()
    )
    canvas.draw(ring, Style(fill=pale, stroke=blue, fill_rule="evenodd"))
    canvas.draw(Rectangle((5, 5), 20, 10), paint)
    canvas.draw(Circle((23, 12), 6), Style(fill=Color(1, 0.6, 0.2), stroke=None))
    return canvas


def main() -> None:
    output = FilePath("examples/output")
    output.mkdir(parents=True, exist_ok=True)
    canvas = gallery()
    canvas.save(output / "gallery.svg", backend="svg")
    canvas.save(output / "gallery.tex", backend="tikz")


if __name__ == "__main__":
    main()
