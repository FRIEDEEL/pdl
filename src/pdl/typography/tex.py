"""Measured native TeX fragments and an explicit XeLaTeX toolchain."""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from functools import lru_cache
from math import isfinite
from pathlib import Path as FilePath
from xml.etree import ElementTree as ET

from pdl.geometry.bounds import Bounds
from pdl.geometry.primitives import Path, Position, point
from pdl.geometry.transforms import Transform, transform_path
from pdl.scene.entity import Entity
from pdl.typography.plain import PT_TO_MM

BP_TO_MM = 25.4 / 72
SVG_NS = "http://www.w3.org/2000/svg"


@dataclass(frozen=True)
class TeXConfig:
    """A document-level environment shared by TeX measurement and native output.

    Args:
        engine: Fragment measurement executable; only ``xelatex`` is supported.
        packages: Package names without options; ``amsmath`` is included by default.
        preamble: Raw LaTeX declarations, including packages requiring options.
        dependencies: External files whose content must participate in cache keys.
        cache_dir: Measurement cache location; ``None`` uses a temporary-root cache.
        cache_salt: Explicit cache invalidation token for external changes.

    Native TikZ content in one document must agree on this environment. Cache keys
    include source and tool versions but do not discover every external package
    or font change; list relevant files and update cache_salt as appropriate.

    Raises:
        ValueError: Engine is unsupported or a package name contains complex syntax.
    """

    engine: str = "xelatex"
    packages: tuple[str, ...] = ("amsmath",)
    preamble: tuple[str, ...] = ()
    dependencies: tuple[str | FilePath, ...] = ()
    cache_dir: str | FilePath | None = None
    cache_salt: str = ""

    def __post_init__(self) -> None:
        if self.engine != "xelatex":
            raise ValueError("Stage 2 supports engine='xelatex' only; no implicit engine fallback.")
        for package in self.packages:
            if not re.fullmatch(r"[A-Za-z0-9_-]+", package):
                raise ValueError("Use preamble entries for package options or complex setup.")

    def latex_preamble(self) -> str:
        return "\n".join(
            [*(rf"\usepackage{{{p}}}" for p in dict.fromkeys(self.packages)), *self.preamble]
        )


@dataclass(frozen=True)
class TeXLayout:
    """TeX box metrics in millimeters plus an SVG fragment and its baseline."""

    width: float
    height: float
    depth: float
    svg: str
    origin_x: float
    origin_y: float

    @property
    def box(self) -> Bounds:
        return Bounds(0, -self.depth, self.width, self.height)


@lru_cache(maxsize=8)
def _tool(name: str) -> tuple[str, str]:
    executable = shutil.which(name)
    if executable is None:
        raise FileNotFoundError(f"Required executable {name!r} is not installed or not on PATH.")
    result = subprocess.run(
        [executable, "--version"], capture_output=True, text=True, check=True, timeout=15
    )
    return executable, result.stdout.splitlines()[0]


def _run(command: list[str], directory: FilePath) -> str:
    try:
        result = subprocess.run(
            command, cwd=directory, capture_output=True, text=True, timeout=60, check=False
        )
    except subprocess.TimeoutExpired as error:
        raise RuntimeError(f"{command[0]} exceeded the 60-second compilation limit.") from error
    output = result.stdout + result.stderr
    if result.returncode:
        raise RuntimeError(f"TeX tool failed: {command[0]}\n{output[-10000:]}")
    return output


def _source(tex: TeX) -> str:
    return (
        r"\documentclass[border=0pt]{standalone}"
        + "\n"
        + tex.environment.latex_preamble()
        + "\n"
        + r"\begin{document}"
        + "\n"
        + rf"\setbox0=\hbox{{{{{tex.latex_body()}}}}}"
        + "\n"
        + r"\typeout{PDL-METRICS:\number\wd0,\number\ht0,\number\dp0}"
        + "\n"
        + r'\special{dvisvgm:raw <g id="pdl-origin" data-x="{?x}" data-y="{?y}"/>}'
        + r"\usebox0"
        + "\n"
        + r"\end{document}"
        + "\n"
    )


def measure(tex: TeX) -> TeXLayout:
    """Compile a fragment once and retain baseline and box metrics together."""
    engine, engine_version = _tool(tex.environment.engine)
    converter, converter_version = _tool("dvisvgm")
    source = _source(tex)
    digest = hashlib.sha256(
        (
            source
            + engine
            + engine_version
            + converter
            + converter_version
            + tex.environment.cache_salt
        ).encode()
    )
    for dependency in tex.environment.dependencies:
        file = FilePath(dependency).resolve()
        digest.update(str(file).encode())
        digest.update(file.read_bytes())
    key = digest.hexdigest()
    root = (
        FilePath(tex.environment.cache_dir)
        if tex.environment.cache_dir is not None
        else FilePath(tempfile.gettempdir()) / "pdl-tex-v1"
    )
    root.mkdir(parents=True, exist_ok=True)
    cached = root / f"{key}.json"
    if cached.is_file():
        return _read_layout(cached.read_text(encoding="utf-8"))
    with tempfile.TemporaryDirectory(prefix="build-", dir=root) as temporary:
        directory = FilePath(temporary)
        (directory / "fragment.tex").write_text(source, encoding="utf-8")
        output = _run(
            [
                engine,
                "-no-pdf",
                "-no-shell-escape",
                "-interaction=nonstopmode",
                "-halt-on-error",
                "fragment.tex",
            ],
            directory,
        )
        metrics = re.search(r"PDL-METRICS:(\d+),(\d+),(\d+)", output)
        if metrics is None:
            raise RuntimeError("TeX did not report box metrics.")
        _run(
            [converter, "--no-fonts=1", "--exact-bbox", "--output=fragment.svg", "fragment.xdv"],
            directory,
        )
        svg = (directory / "fragment.svg").read_text(encoding="utf-8")
        element = ET.fromstring(svg)
        marker = element.find(".//*[@id='pdl-origin']")
        if marker is None:
            empty = all(int(metrics[i]) == 0 for i in (1, 2, 3)) and not any(
                el.tag.rsplit("}", 1)[-1] in ("path", "rect", "image", "use")
                for el in element.iter()
            )
            if not empty:
                raise RuntimeError("SVG converter did not retain the TeX baseline marker.")
            origin_x = origin_y = 0.0
        else:
            origin_x = float(marker.attrib["data-x"])
            origin_y = float(marker.attrib["data-y"])
        values = {
            "width": int(metrics[1]) / 65536 * PT_TO_MM,
            "height": int(metrics[2]) / 65536 * PT_TO_MM,
            "depth": int(metrics[3]) / 65536 * PT_TO_MM,
            "origin_x": origin_x,
            "origin_y": origin_y,
            "svg": svg,
        }
        serialized = json.dumps(values)
        pending = directory / "cache.json"
        pending.write_text(serialized, encoding="utf-8")
        pending.replace(cached)
        return _read_layout(serialized)


def _read_layout(serialized: str) -> TeXLayout:
    # JSON is private cache data. Validate its shape before using it.
    data: object = json.loads(serialized)
    if not isinstance(data, dict):
        raise ValueError("Invalid TeX cache record.")
    from typing import cast

    fields = cast(dict[str, object], data)
    numbers: list[float] = []
    for name in ("width", "height", "depth", "origin_x", "origin_y"):
        value = fields.get(name)
        if not isinstance(value, (int, float)) or not isfinite(value):
            raise ValueError(f"Invalid TeX cache field: {name}")
        numbers.append(float(value))
    svg = fields.get("svg")
    if not isinstance(svg, str):
        raise ValueError("Invalid cached SVG.")
    return TeXLayout(numbers[0], numbers[1], numbers[2], svg, numbers[3], numbers[4])


@dataclass(eq=False)
class TeX(Entity):
    """LaTeX source typeset at a baseline position.

    Args:
        source: LaTeX content; include ``$...$`` or other delimiters for math.
            Python raw strings preserve backslashes conveniently.
        position: Left baseline reference in local millimeters.
        size: Positive font size in TeX points (1/72.27 inch).
        config: Explicit TeX environment, or the renderer's default environment.

    Measurement requires XeLaTeX and dvisvgm, even when requesting TikZ source
    without a final PDF. SVG embeds a converted fragment; TikZ retains native
    LaTeX source. Shared native documents require compatible TeXConfig values.
    Supply only fill paint, with ``stroke=None``, when setting a style.
    """

    source: str
    position: Position = (0, 0)
    size: float = 12
    config: TeXConfig | None = None

    def __post_init__(self) -> None:
        point(self.position)
        if not isfinite(self.size) or self.size <= 0:
            raise ValueError("TeX size must be positive and finite.")

    @property
    def environment(self) -> TeXConfig:
        from pdl.rendering.config import current_renderer

        return self.config or current_renderer().tex or TeXConfig()

    def latex_body(self) -> str:
        return (
            rf"\fontsize{{{self.size:.12g}}}{{{self.size * 1.25:.12g}}}\selectfont " + self.source
        )

    @property
    def layout(self) -> TeXLayout:
        return measure(self)

    @property
    def layout_bounds(self) -> Bounds:
        p = point(self.position)
        return self.layout.box.transformed(Transform.translate(p.x, p.y))

    def to_path(self) -> Path:
        """Lower monochrome TeX outlines; general SVG artwork is not supported."""
        from pdl.typography.tex_svg import outline_path

        p = point(self.position)
        return transform_path(outline_path(self.layout), Transform.translate(p.x, p.y))
