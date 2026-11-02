"""Literal multilingual labels and optional layout/baseline overlays."""

from examples._shared import LABEL, chinese_font, cjk_font, export, latin_font
from pdl import Canvas, text
from pdl.extensions.diagram.debug import debug_overlay

SHOW_DEBUG = True


def example() -> Canvas:
    latin, cjk = latin_font(), cjk_font()
    title = text("Text / explicit fonts and measured baselines", latin, (8, 103), size=16)
    english = text("AV fi cafe\u0301 — 50% & $", latin, (10, 84), size=17)
    chinese = text("真空系统：压力与流量", chinese_font(), (10, 65), size=15)
    japanese = text("真空系统と流量", position=(10, 46), size=15)
    multiline = text(
        "Centered multiline label\nshort line",
        latin,
        (120, 25),
        size=12,
        align="center",
        line_spacing=1.5,
    )
    note = text("Green: layout box / baseline. Red: outer bounds / anchors.", latin, (8, 5), size=9)
    canvas = Canvas(180, 115, fonts=(cjk, chinese_font()))
    canvas.draw(title, LABEL)
    for text_entity in (english, chinese, japanese, multiline):
        canvas.draw(text_entity, LABEL)
        if SHOW_DEBUG:
            canvas.draw(debug_overlay(text_entity))
    fallback_caption = text("JP -> CN fallback", latin, (110, 46), size=10)
    canvas.draw(fallback_caption, LABEL)
    canvas.draw(note, LABEL)
    return canvas


if __name__ == "__main__":
    export(example(), __file__)
