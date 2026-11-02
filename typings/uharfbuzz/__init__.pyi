# Minimal declarations for the HarfBuzz API used by pdl.
# The installed uharfbuzz version exposes these dynamically through its extension.
class Face:
    def __init__(self, blob: bytes, index: int = 0) -> None: ...
    upem: int

class FontExtents:
    ascender: int
    descender: int
    line_gap: int

class Font:
    def __init__(self, face: Face) -> None: ...
    scale: tuple[int, int]
    def get_font_extents(self, direction: str) -> FontExtents: ...

class GlyphInfo:
    codepoint: int

class GlyphPosition:
    x_advance: int
    y_advance: int
    x_offset: int
    y_offset: int

class Buffer:
    def __init__(self) -> None: ...
    def add_str(self, text: str) -> None: ...
    def guess_segment_properties(self) -> None: ...
    glyph_infos: list[GlyphInfo]
    glyph_positions: list[GlyphPosition]

def shape(font: Font, buffer: Buffer) -> None: ...
