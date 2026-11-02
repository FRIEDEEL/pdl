"""Submission capture, paint ordering, viewport policy, and export entrypoints."""

from __future__ import annotations

from collections.abc import Generator
from contextlib import AbstractContextManager, contextmanager
from math import isfinite, sqrt
from pathlib import Path as FilePath
from typing import Literal, Self

from pdl.author.entity.base import Entity
from pdl.author.entity.capture import Composite, freeze, walk
from pdl.author.entity.group import Group
from pdl.author.geometry.bounds import Bounds
from pdl.author.geometry.frame import WORLD, Frame
from pdl.author.geometry.image import Image
from pdl.author.style import Font, Style
from pdl.author.style.typography import RendererConfig, rendering
from pdl.author.transform.affine import AffineTransform, Scaling, Translation
from pdl.backends.svg.document import render as svg_render
from pdl.backends.tikz.compiler import TikZMode, compile_pdf
from pdl.backends.tikz.document import render as tikz_render
from pdl.backends.tikz.text import preamble
from pdl.canvas.layers import Layer, LayerStack, valid_integer
from pdl.canvas.query import Query
from pdl.canvas.records import Viewport

type Backend = Literal["svg", "tikz"]


class Canvas:
    """Capture Entities in millimeters, with a lower-left origin and y pointing up.

    Submissions capture geometry, effective paint, and typography immediately.
    Subsequent edits require another submission. Layer order is resolved when
    rendering. Auto-size and fit use logical bounds plus conservative stroke
    margins; stroke widths stay in final output millimeters.
    """

    def __init__(
        self,
        width: float | None = None,
        height: float | None = None,
        *,
        fonts: tuple[Font, ...] = (),
        mode: Literal["clip", "fit", "auto_size"] = "clip",
        padding: float = 0,
        backend: Backend = "svg",
        renderer: RendererConfig | None = None,
    ) -> None:
        if mode not in ("clip", "fit", "auto_size"):
            raise ValueError("Unknown canvas mapping mode.")
        if not isfinite(padding) or padding < 0:
            raise ValueError("Padding must be finite and nonnegative.")
        if mode != "auto_size" and (width is None or height is None):
            raise ValueError("Fixed canvases require width and height.")
        self.width = 1 if width is None else width
        self.height = 1 if height is None else height
        if not all(isfinite(v) and v > 0 for v in (self.width, self.height)):
            raise ValueError("Canvas dimensions must be positive and finite.")
        if backend not in ("svg", "tikz"):
            raise ValueError("Unknown backend.")
        self.mode, self.padding, self.backend = mode, padding, backend
        self.renderer = renderer or RendererConfig(fonts=fonts)
        self.layers = LayerStack()
        self._records: list[tuple[Layer, Entity]] = []
        self._world = AffineTransform()
        self._mappings: dict[Frame, AffineTransform] = {}

    @property
    def drawings(self) -> tuple[Entity, ...]:
        return tuple(
            d for _, d in sorted(self._records, key=lambda record: self.layers.index(record[0]))
        )

    def map(self, space: Frame, transform: AffineTransform) -> None:
        """Set explicit query-frame conversion, or the final WORLD page mapping."""
        if space is WORLD:
            self._world = transform
        else:
            self._mappings[space] = transform

    def frame_mapping(self, space: Frame) -> AffineTransform:
        return self._mappings.get(space, space.matrix)

    def typography(self, fonts: tuple[Font, ...] | None = None) -> AbstractContextManager[None]:
        return rendering(
            self.renderer if fonts is None else RendererConfig(fonts=fonts, tex=self.renderer.tex)
        )

    @contextmanager
    def evaluation(self) -> Generator[None, None, None]:
        with self.typography():
            yield

    def snapshot(self, graphic: Entity | Composite, *, style: Style | None = None) -> Entity:
        """Capture a root override while preserving explicit member styles."""
        with self.typography():
            if style is not None:
                target = (
                    graphic.copy().set_style(style)
                    if isinstance(graphic, Entity)
                    else Group(*graphic.decompose(), style=style)
                )
                return freeze(target)
            return freeze(graphic)

    def draw(self, graphic: Entity | Composite, style: Style | None = None) -> None:
        if isinstance(graphic, Entity) and graphic.parent is not None:
            raise ValueError("Draw the outermost Group rather than an owned member.")
        layer = graphic.layer if isinstance(graphic, Entity) else 0
        automatic = not isinstance(graphic, Entity) or graphic.automatic_layer
        if isinstance(layer, Layer) and automatic:
            layer = layer.position
        if valid_integer(layer):
            assert isinstance(layer, int)
            selected = self.layers[layer]
        elif isinstance(layer, Layer):
            selected = self.layers.adopt(layer)
        else:
            raise TypeError("Expected an integer layer or Canvas Layer.")
        if isinstance(graphic, Entity):
            graphic.bind_layer(selected, automatic=automatic)
        captured = self.snapshot(graphic, style=style)
        self._records.append((selected, captured))

    def add(self, *graphics: Entity | Composite) -> Self:
        for graphic in graphics:
            self.draw(graphic)
        return self

    def query(self) -> Query:
        return Query(self)

    def bounds(self, graphic: Entity | Composite) -> Bounds:
        return self.query().bounds(graphic)

    @staticmethod
    def _stroke_margin(style: Style) -> float:
        if style.stroke is None or style.line_width == 0:
            return 0
        return style.line_width / 2 * max(sqrt(2), 10 if style.line_join == "miter" else 1)

    def _viewport(
        self, source: tuple[Entity, ...] | None = None
    ) -> tuple[Viewport, AffineTransform]:
        drawings = tuple(
            d.copy().apply_transform(self._world)
            for d in (self.drawings if source is None else source)
        )
        box = Bounds.empty()
        for drawing in drawings:
            box = box.union(drawing.bounds)
        width, height = self.width, self.height
        placement = AffineTransform()
        if self.mode != "clip" and not box.is_empty:
            allowance = max(
                (self._stroke_margin(d.effective_style) for d in walk(drawings)), default=0
            )
            if self.mode == "auto_size":
                expanded = box.expanded(allowance)
                width = max(expanded.width + 2 * self.padding, 1e-6)
                height = max(expanded.height + 2 * self.padding, 1e-6)
                placement = Translation(
                    self.padding - expanded.left, self.padding - expanded.bottom
                )
            else:
                available_w = width - 2 * (self.padding + allowance)
                available_h = height - 2 * (self.padding + allowance)
                if min(available_w, available_h) <= 0:
                    raise ValueError("Canvas padding and stroke leave no fitting area.")
                ratios = [
                    size / extent
                    for size, extent in ((available_w, box.width), (available_h, box.height))
                    if extent > 0
                ]
                scale = min(ratios, default=1)
                center = box.anchor()
                placement = (
                    Translation(width / 2, height / 2)
                    @ Scaling(scale)
                    @ Translation(-center.x, -center.y)
                )
        for drawing in drawings:
            drawing.apply_transform(placement)
        return Viewport(width, height, drawings), placement @ self._world

    def viewport(self, source: tuple[Entity, ...] | None = None) -> Viewport:
        return self._viewport(source)[0]

    @property
    def output_transform(self) -> AffineTransform:
        return self._viewport()[1]

    def render(
        self,
        backend: Backend | None = None,
        *,
        standalone: bool = True,
        fonts: tuple[Font, ...] | None = None,
        renderer: RendererConfig | None = None,
    ) -> str:
        context = rendering(renderer) if renderer is not None else self.typography(fonts)
        selected = self.backend if backend is None else backend
        with context:
            page = self.viewport()
            if selected == "svg":
                return svg_render(page)
            if selected == "tikz":
                return tikz_render(page, standalone=standalone)
            raise ValueError(f"Unknown backend: {selected}")

    def latex_preamble(self) -> str:
        with self.typography():
            return preamble(tuple(walk(self.viewport().drawings)))

    def save(
        self,
        filename: str | FilePath,
        *,
        backend: Backend | None = None,
        fonts: tuple[Font, ...] | None = None,
        renderer: RendererConfig | None = None,
        tikz_mode: TikZMode = "auto",
        keep_intermediates: bool = False,
        engine: str = "xelatex",
    ) -> None:
        if tikz_mode not in ("auto", "tex", "pdf"):
            raise ValueError(f"Unknown TikZ output mode: {tikz_mode}")
        selected = self.backend if backend is None else backend
        source = FilePath(filename)
        content = self.render(backend, fonts=fonts, renderer=renderer)
        if selected == "tikz":
            for drawing in walk(self.drawings):
                if isinstance(drawing.geometry, Image):
                    image = drawing.geometry
                    asset = image.asset(source.parent / (source.stem + "-assets"))
                    content = content.replace(
                        image.asset().as_posix(),
                        asset.relative_to(source.parent.resolve()).as_posix(),
                    )
        source.write_text(content, encoding="utf-8")
        if selected == "tikz":
            compile_pdf(
                source, mode=tikz_mode, keep_intermediates=keep_intermediates, engine=engine
            )
