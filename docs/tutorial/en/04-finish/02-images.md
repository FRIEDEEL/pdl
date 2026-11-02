# 4.2 Embed an image

Image captures local PNG/JPEG bytes at construction and describes a viewport in millimeters. Contain preserves the full source, cover crops to fill the viewport, and stretch changes aspect ratio.

Affine edits bake current viewport corners and preserve the pixels. SVG embeds a data URL; saved TikZ copies content-addressed assets beside the source, allowing the output directory to be moved. DPI, EXIF orientation, pixel decoding, SVG/PDF import, and perspective image warping are outside this interface.

## Runnable examples and output

```{literalinclude} ../../../../examples/tutorial/media/images.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![19. Embed an image](../../../../examples/output/tutorial/media/images.svg)

Full source: [images.py](../../../../examples/tutorial/media/images.py).

---

[Part contents](index.md)
