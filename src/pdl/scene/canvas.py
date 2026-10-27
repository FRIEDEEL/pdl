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
from pdl.rendering.tikz.compiler import TikZMode, compile_pdf
from pdl.scene.authoring import Entity, capture
from pdl.scene.composition import Drawing, Graphic
from pdl.scene.composition import bounds as scene_bounds
from pdl.scene.layers import Layer, LayerStack
from pdl.scene.paint import BLACK as BLACK
from pdl.scene.paint import Color as Color
from pdl.scene.paint import Style as Style
from pdl.scene.resolved import Query, ResolvedGraphic, resolve_geometry
from pdl.scene.spaces import WORLD, CoordinateSystem, space_mappings
from pdl.typography.plain import Font


class Canvas:
    """An ordered drawing area with millimeter coordinates and SVG/TikZ output.

    Args:
        width: Canvas width in millimeters; required except in ``auto_size`` mode.
        height: Canvas height in millimeters; required except in ``auto_size`` mode.
        fonts: Explicit default fonts, used if ``renderer`` is not supplied.
        mode: ``clip`` keeps a fixed viewport; ``fit`` scales and centers content;
            ``auto_size`` preserves scale and derives dimensions from content.
        padding: Nonnegative millimeter margin for fit/auto-size.
        backend: Default output adapter: ``svg`` or ``tikz``.
        renderer: Font and TeX policy; takes precedence over ``fonts``.

    The origin is at the lower-left, x points right, and y points up. Later
    ``draw`` records paint over earlier ones. Text scales with geometry, but
    stroke widths remain in final Canvas millimeters. Fitting uses layout bounds
    and conservative stroke margins rather than exact painted contours.

    Raises:
        ValueError: Dimensions, padding, or viewport mode are invalid.
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
        self.layers = LayerStack()
        self._drawing_layers: list[Layer] = []

    @property
    def drawings(self) -> tuple[Drawing, ...]:
        if not self._drawing_layers:
            return tuple(self._drawings)
        return tuple(
            d
            for _, d in sorted(
                zip(self._drawing_layers, self._drawings, strict=True),
                key=lambda record: self.layers.index(record[0]),
            )
        )

    def map(self, space: CoordinateSystem, transform: Transform) -> None:
        """Override a frame's local-to-parent matrix for this canvas.

        Args:
            space: Authoring frame. ``WORLD`` sets the world-to-Canvas base mapping.
            transform: Replacement matrix, not an additional composed transform.

        The frame itself and other canvases are not changed.
        """
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
        """Return a query helper using this canvas's current fonts and mappings.

        Queries measure values without adding anything to the drawing list.
        """
        return Query(self)

    def resolve(self, graphic: Graphic | Drawing) -> ResolvedGraphic:
        """Measure an object and return a detached snapshot in Canvas coordinates.

        Args:
            graphic: Object or placed Drawing to resolve; it is not added to the canvas.

        Returns:
            Fixed geometry, placements, and typography metrics. Native shape/text
            identities are retained when possible. Native text output still needs fonts
            or TeX resources; this is not a self-contained image file.

        With fit/auto-size, the paint list determines the viewport. If it is empty,
        the requested object supplies the fitting bounds.
        """
        with self.evaluation():
            root = capture(graphic if isinstance(graphic, Drawing) else Drawing(graphic))
            result = resolve_geometry(root)
            view = self.viewport(self.drawings or (root,))
            return ResolvedGraphic(
                tuple(d.transformed(view.output_transform) for d in result.decompose())
            )

    def draw(self, geometry: Graphic | Drawing, style: Style | None = None) -> None:
        """Add an object to the end of the paint order without rendering it.

        Args:
            geometry: Shape, text, composite, Entity, or explicitly placed Drawing.
            style: Optional paint override for this draw record.

        Built-in mutable paths and Entity states are captured now; later edits
        require another draw call. Font-dependent positions are measured later.
        Referencing an object does not draw it automatically.
        """
        from pdl.scene.composition import Group
        from pdl.scene.gather import Gather

        if isinstance(geometry, (Layer, Gather)):
            raise TypeError("Canvas.draw requires a graphic, not a Layer or Gather.")
        target = geometry.geometry if isinstance(geometry, Drawing) else geometry
        if isinstance(target, (Entity, Group)) and target.root is not target:
            raise ValueError("Draw the outermost Group, not an individual grouped member.")
        layer = target.layer if isinstance(target, (Entity, Group)) else 0
        selected = self.layers[layer] if isinstance(layer, int) else self.layers.adopt(layer)
        if isinstance(target, (Entity, Group)):
            target.set_layer(selected)
        geometry = capture(geometry)
        self._drawing_layers.append(selected)
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
        """Return layout/geometry bounds in final Canvas coordinates, excluding stroke.

        Args:
            graphic: Object to measure; it need not have been drawn.

        Returns:
            Axis-aligned bounds. For authoring coordinates instead, use
            ``canvas.query().bounds(graphic, in_space=WORLD)``.
        """
        return self.query().bounds(graphic)

    def render(
        self,
        backend: Literal["svg", "tikz"] | None = None,
        *,
        standalone: bool = True,
        fonts: tuple[Font, ...] | None = None,
        renderer: RendererConfig | None = None,
    ) -> str:
        """Return SVG or TikZ source without writing a file.

        Args:
            backend: Output adapter; ``None`` uses the canvas default.
            standalone: Include a complete TikZ document when true; ignored by SVG.
            fonts: Per-call font override when ``renderer`` is absent.
            renderer: Per-call font/TeX configuration, taking precedence over ``fonts``.

        Returns:
            SVG XML or TeX source. Each call reevaluates dependencies and typography.

        Raises:
            ValueError: The adapter or paint/configuration is unsupported.
            FileNotFoundError: Required fonts or TeX measurement tools are missing.
            RuntimeError: TeX measurement fails.

        Even source-only TikZ output measures Text/TeX first; rendering a TeX object
        can therefore invoke external tools. This method does not compile a final PDF.
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
        from pdl.scene.composition import GroupDescription as Group

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
        renderer: RendererConfig | None = None,
        tikz_mode: TikZMode = "auto",
        keep_intermediates: bool = False,
        engine: str = "xelatex",
    ) -> None:
        """Write source and optionally compile a TikZ PDF beside it.

        Args:
            filename: Source destination; parent directories must already exist.
                Use ``.svg`` for SVG and ``.tex`` for TikZ. The suffix does not select
                the backend.
            backend: Adapter override, or the canvas default.
            fonts: Per-call font override when ``renderer`` is absent.
            renderer: Per-call font/TeX configuration.
            tikz_mode: ``auto`` compiles if the engine exists; ``tex`` saves only source;
                ``pdf`` requires successful PDF compilation. Ignored by SVG.
            keep_intermediates: Keep TeX auxiliary files beside source when true.
            engine: Executable used for final PDF compilation, default ``xelatex``.
                TeX fragment measurement is configured separately by ``TeXConfig``.

        Missing compilers are tolerated only in auto mode. An available compiler
        that fails always raises an error. By default compilation uses a temporary
        folder and copies back the PDF without deleting existing auxiliary files.

        Raises:
            FileNotFoundError: The output parent or a required tool/font is missing.
            RuntimeError: External compilation or TeX measurement fails.
            ValueError: A rendering option or TikZ mode is invalid.
        """
        if tikz_mode not in ("auto", "tex", "pdf"):
            raise ValueError(f"Unknown TikZ output mode: {tikz_mode}")
        selected = self.backend if backend is None else backend
        source = FilePath(filename)
        source.write_text(self.render(backend, fonts=fonts, renderer=renderer), encoding="utf-8")
        if selected == "tikz":
            compile_pdf(
                source, mode=tikz_mode, keep_intermediates=keep_intermediates, engine=engine
            )
