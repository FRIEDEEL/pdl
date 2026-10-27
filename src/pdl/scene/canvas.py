"""Ordered drawing container and backend-independent paint."""

from __future__ import annotations

from collections.abc import Generator
from contextlib import AbstractContextManager, contextmanager
from math import isfinite
from pathlib import Path as FilePath
from typing import Literal

from pdl.geometry.bounds import Bounds
from pdl.geometry.transforms import Transform
from pdl.rendering.config import RendererConfig, rendering
from pdl.scene.authoring import capture
from pdl.scene.composition import Drawing, Graphic
from pdl.scene.composition import bounds as scene_bounds
from pdl.scene.paint import BLACK as BLACK
from pdl.scene.paint import Color as Color
from pdl.scene.paint import Style as Style
from pdl.scene.resolved import Query, ResolvedGraphic, resolve_geometry
from pdl.scene.spaces import WORLD, CoordinateSystem, space_mappings
from pdl.typography.plain import Font


class Canvas:
    """An ordered drawing document with explicit viewport adaptation.

    Coordinates are Cartesian millimeters. draw captures authoring state,
    render resolves dependencies, and later records paint above earlier ones.
    The default clip policy retains the fixed bottom-left-origin viewport.
    """

    def __init__(
        self,
        width: float | None = None,
        height: float | None = None,
        *,
        fonts: tuple[Font, ...] = (),
        mode: Literal["clip", "fit", "auto_size"] = "clip",
        padding: float = 0,
        backend: Literal["svg", "tikz"] = "svg",
        renderer: RendererConfig | None = None,
    ) -> None:
        if mode not in ("clip", "fit", "auto_size"):
            raise ValueError("Unknown canvas mapping mode.")
        if not isfinite(padding) or padding < 0:
            raise ValueError("Padding must be finite and nonnegative.")
        if mode != "auto_size" and (width is None or height is None):
            raise ValueError("Fixed canvases require width and height.")
        width = 1 if width is None else width
        height = 1 if height is None else height
        if not all(isfinite(v) and v > 0 for v in (width, height)):
            raise ValueError("Canvas dimensions must be positive and finite.")
        self.mode = mode
        self.padding = padding
        self.backend = backend
        self.output_transform = Transform()
        self._world_transform = Transform()
        self._space_mappings: dict[CoordinateSystem, Transform] = {}
        self.width = width
        self.height = height
        self.renderer = renderer or RendererConfig(fonts=fonts)
        self._drawings: list[Drawing] = []

    @property
    def drawings(self) -> tuple[Drawing, ...]:
        return tuple(self._drawings)

    def map(self, space: CoordinateSystem, transform: Transform) -> None:
        """Set a frame's local-to-parent mapping for this canvas."""
        if space is WORLD:
            self._world_transform = transform
        else:
            self._space_mappings[space] = transform

    @contextmanager
    def evaluation(self) -> Generator[None, None, None]:
        """Establish canvas resources and coordinate mappings for one operation."""
        token = space_mappings.set(self._space_mappings.copy())
        try:
            with self.typography():
                yield
        finally:
            space_mappings.reset(token)

    def query(self) -> Query:
        return Query(self)

    def resolve(self, graphic: Graphic | Drawing) -> ResolvedGraphic:
        """Return a detached numerical snapshot in final canvas coordinates."""
        with self.evaluation():
            root = capture(graphic if isinstance(graphic, Drawing) else Drawing(graphic))
            result = resolve_geometry(root)
            view = self.viewport(self.drawings or (root,))
            return ResolvedGraphic(
                tuple(d.transformed(view.output_transform) for d in result.decompose())
            )

    def draw(self, geometry: Graphic | Drawing, style: Style | None = None) -> None:
        """Capture authoring state without measuring fonts or flattening geometry."""
        geometry = capture(geometry)
        if isinstance(geometry, Drawing):
            if style is not None:
                geometry = Drawing(geometry.geometry, style, geometry.transform)
            self._drawings.append(geometry)
        else:
            self._drawings.append(Drawing(geometry, style))

    def typography(self, fonts: tuple[Font, ...] | None = None) -> AbstractContextManager[None]:
        """Use the canvas policy for explicitly requested measurements."""
        return rendering(
            self.renderer if fonts is None else RendererConfig(fonts=fonts, tex=self.renderer.tex)
        )

    def bounds(self, graphic: Graphic | Drawing) -> Bounds:
        """Measure geometry or layout using this canvas's font policy."""
        return self.query().bounds(graphic)

    def render(
        self,
        backend: Literal["svg", "tikz"] | None = None,
        *,
        standalone: bool = True,
        fonts: tuple[Font, ...] | None = None,
        renderer: RendererConfig | None = None,
    ) -> str:
        """Export with optional ordered defaults for Text without an explicit font.

        Content sizes and anchor references are evaluated for this invocation.
        Changing export fonts also recomputes dependent connection endpoints.
        """
        from pdl.rendering.svg.document import render as svg_render
        from pdl.rendering.tikz.document import render as tikz_render

        context = rendering(renderer) if renderer is not None else self.typography(fonts)
        selected = self.backend if backend is None else backend
        token = space_mappings.set(self._space_mappings.copy())
        try:
            with context:
                view = self.viewport()
                if selected == "svg":
                    return svg_render(view)
                if selected == "tikz":
                    return tikz_render(view, standalone=standalone)
                raise ValueError(f"Unknown backend: {selected}")
        finally:
            space_mappings.reset(token)

    def viewport(self, source: tuple[Drawing, ...] | None = None) -> Canvas:
        """Resolve authoring mappings, then choose the final output viewport."""
        from pdl.scene.composition import Group

        roots = self.drawings if source is None else source
        drawings = resolve_geometry(Group(roots)).decompose() if roots else ()
        drawings = tuple(d.transformed(self._world_transform) for d in drawings)
        placement = Transform()
        width, height = self.width, self.height
        if self.mode != "clip" and drawings and not scene_bounds(Group(drawings)).is_empty:
            box = scene_bounds(Group(drawings))
            # Geometry/layout bounds plus a conservative stroke allowance.
            from pdl.scene.composition import walk

            allowance = max(
                (self._stroke_margin(d.style or Style()) for d in walk(drawings)), default=0
            )
            box = box.expanded(allowance)
            if self.mode == "auto_size":
                width = max(box.width + 2 * self.padding, 1e-6)
                height = max(box.height + 2 * self.padding, 1e-6)
                placement = Transform.translate(self.padding - box.left, self.padding - box.bottom)
            else:
                available_w = width - 2 * (self.padding + allowance)
                available_h = height - 2 * (self.padding + allowance)
                if min(available_w, available_h) <= 0:
                    raise ValueError("Canvas padding and stroke leave no fitting area.")
                raw = scene_bounds(Group(drawings))
                ratios = [
                    size / extent
                    for size, extent in ((available_w, raw.width), (available_h, raw.height))
                    if extent > 0
                ]
                scale = min(ratios, default=1)
                center = raw.anchor()
                placement = (
                    Transform.translate(width / 2, height / 2)
                    @ Transform.scale(scale)
                    @ Transform.translate(-center.x, -center.y)
                )
        view = Canvas(width, height, renderer=self.renderer)
        view.output_transform = placement @ self._world_transform
        view._drawings = [d.transformed(placement) for d in drawings]
        return view

    @staticmethod
    def _stroke_margin(style: Style) -> float:
        if style.stroke is None:
            return 0
        # Miter joins and square caps can extend beyond half a line width.
        from math import sqrt

        return style.line_width / 2 * max(sqrt(2), 10 if style.line_join == "miter" else 1)

    def latex_preamble(self) -> str:
        """Return required packages and macros for an embedded TikZ fragment."""
        from pdl.rendering.tikz.nodes import supports
        from pdl.rendering.tikz.text import preamble
        from pdl.rendering.traversal import prepare

        with self.evaluation():
            return preamble(tuple(prepare(self.viewport().drawings, supports)))

    def save(
        self,
        filename: str | FilePath,
        *,
        backend: Literal["svg", "tikz"] | None = None,
        fonts: tuple[Font, ...] | None = None,
    ) -> None:
        """Write the selected output as UTF-8 text."""
        FilePath(filename).write_text(self.render(backend, fonts=fonts), encoding="utf-8")
