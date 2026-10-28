"""Native TeX node rendering and document environment collection."""

from collections.abc import Iterator
from pathlib import Path as FilePath

from pdl.author.composition import Drawing
from pdl.author.style import BLACK, Color, Style
from pdl.author.tex import TeX
from pdl.author.text import Text
from pdl.backends.formatting import number
from pdl.backends.tikz.geometry import color, coordinate
from pdl.foundation.geometry.primitives import point
from pdl.foundation.typography.config import current_renderer
from pdl.foundation.typography.shaping import Font
from pdl.foundation.typography.tex import TeXConfig


def resources(drawings: tuple[Drawing, ...]) -> Iterator[Text | TeX]:
    """Inspect native object content without decomposing supported objects."""
    for drawing in drawings:
        geometry = drawing.geometry
        if isinstance(geometry, (Text, TeX)):
            yield geometry


def configuration(drawings: tuple[Drawing, ...]) -> TeXConfig | None:
    configs = {text.environment for text in resources(drawings) if isinstance(text, TeX)}
    if len(configs) > 1:
        raise ValueError("One native TikZ document requires a shared TeXConfig.")
    explicit = current_renderer().tex
    if explicit is not None:
        configs.add(explicit)
    if len(configs) > 1:
        raise ValueError("One native TikZ document requires a shared TeXConfig.")
    if configs:
        return next(iter(configs))
    return TeXConfig() if any(isinstance(text, Text) for text in resources(drawings)) else None


def font_commands(drawings: tuple[Drawing, ...]) -> dict[Font, str]:
    result: dict[Font, str] = {}
    for text in resources(drawings):
        if isinstance(text, Text):
            for run in text.layout.runs:
                if run.font not in result:
                    index = len(result)
                    letters = ""
                    while True:
                        letters = chr(65 + index % 26) + letters
                        index = index // 26 - 1
                        if index < 0:
                            break
                    result[run.font] = "pdlfont" + letters
    return result


def preamble(drawings: tuple[Drawing, ...]) -> str:
    config = configuration(drawings)
    lines = [r"\usepackage{tikz}", r"\usepackage{graphicx}"]
    if config:
        lines.append(config.latex_preamble())
    commands = font_commands(drawings)
    if commands:
        lines.append(r"\usepackage{fontspec}")
    for font, command in commands.items():
        file = FilePath(font.file).resolve()
        if any(c in str(file) for c in "%#{}\\"):
            raise ValueError("Font paths with TeX special characters are not supported.")
        lines.append(
            rf"\newfontfamily\{command}[Path={{{file.parent.as_posix()}/}},"
            rf"FontIndex={font.index}]{{{file.name}}}"
        )
    return "\n".join(lines) + "\n"


def _escape_text(text: str) -> str:
    replacements = {
        "\\": r"\textbackslash{}",
        "{": r"\{",
        "}": r"\}",
        "$": r"\$",
        "&": r"\&",
        "#": r"\#",
        "%": r"\%",
        "_": r"\_",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(character, character) for character in text)


def render_text(text: Text, drawing: Drawing, commands: dict[Font, str]) -> str:
    """Emit native LaTeX text; font shaping belongs to the TeX engine."""
    paint = drawing.style or Style(stroke=None, fill=BLACK)
    if paint.stroke is not None:
        raise ValueError("Native Text supports fill-only paint; use fill and stroke=None.")
    if paint.fill is None:
        return ""
    if not isinstance(paint.fill, Color):
        raise ValueError("Native Text and TeX require solid color fills.")
    t = drawing.transform
    if t.a * t.d - t.b * t.c == 0:
        return ""
    a, b, c, d, e, f = (number(v) for v in t.values)
    lines = [f"\\begin{{scope}}[cm={{{a},{b},{c},{d},({e},{f})}},transform shape]"]
    p = point(text.position)
    for run in text.layout.runs:
        position = coordinate(type(p)(p.x + run.x, p.y + run.y))
        body = (
            rf"\{commands[run.font]}\fontsize{{{number(text.size)}}}"
            rf"{{{number(text.size * text.line_spacing)}}}\selectfont " + _escape_text(run.text)
        )
        lines.append(
            f"\\node[anchor=base west,inner sep=0pt,outer sep=0pt,text={color(paint.fill)},"
            f"text opacity={number(paint.opacity)}] "
            f"at {position} {{{body}}};"
        )
    lines.append(r"\end{scope}")
    return "\n".join(lines)


def render_tex(tex: TeX, drawing: Drawing) -> str:
    t = drawing.transform
    if t.a * t.d - t.b * t.c == 0:
        return ""
    paint = drawing.style or Style(stroke=None, fill=BLACK)
    if paint.stroke is not None:
        raise ValueError("Native TeX supports fill-only paint; use Style(stroke=None, fill=...).")
    if paint.fill is None:
        return ""
    if not isinstance(paint.fill, Color):
        raise ValueError("Native Text and TeX require solid color fills.")
    a, b, c, d, e, f = (number(v) for v in drawing.transform.values)
    return (
        f"\\begin{{scope}}[cm={{{a},{b},{c},{d},({e},{f})}},transform shape]\n"
        + f"\\node[anchor=base west,inner sep=0pt,outer sep=0pt,text={color(paint.fill)},"
        f"text opacity={number(paint.opacity)}] "
        + f"at {coordinate(point(tex.position))} {{{tex.latex_body()}}};\n"
        + r"\end{scope}"
    )
