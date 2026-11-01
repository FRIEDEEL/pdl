"""Editable LaTeX content backed by shared TeX measurement."""

from __future__ import annotations

from dataclasses import dataclass, field
from math import isfinite

from pdl.author.entity import Entity
from pdl.foundation.geometry.bounds import Bounds
from pdl.foundation.geometry.primitives import Path, Position, point
from pdl.foundation.geometry.transforms import Transform, transform_path
from pdl.foundation.typography.tex import TeXConfig, TeXLayout, measure
from pdl.foundation.typography.tex_svg import outline_path


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

    _measurement: TeXLayout | None = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        point(self.position)
        if not isfinite(self.size) or self.size <= 0:
            raise ValueError("TeX size must be positive and finite.")

    @property
    def environment(self) -> TeXConfig:
        from pdl.foundation.typography.config import current_renderer

        return self.config or current_renderer().tex or TeXConfig()

    def latex_body(self) -> str:
        return (
            rf"\fontsize{{{self.size:.12g}}}{{{self.size * 1.25:.12g}}}\selectfont " + self.source
        )

    @property
    def layout(self) -> TeXLayout:
        if self.description_only and self._measurement is not None:
            return self._measurement
        return measure(self)

    def capture_layout(self) -> None:
        """Fix measured layout on a captured description before output."""
        self.config = self.environment
        self._measurement = self.layout

    @property
    def layout_bounds(self) -> Bounds:
        p = point(self.position)
        return self.layout.box.transformed(Transform.translate(p.x, p.y))

    def to_path(self) -> Path:
        """Lower monochrome TeX outlines; general SVG artwork is not supported."""
        p = point(self.position)
        return transform_path(outline_path(self.layout), Transform.translate(p.x, p.y))
