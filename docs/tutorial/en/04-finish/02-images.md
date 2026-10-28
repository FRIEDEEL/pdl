# 4.2 Embed an image

Image accepts a local PNG or JPEG. In this example `image_file` points to
[the four-color source image](../../../../examples/tutorial/media/quadrants.png);
the complete script resolves this path beside itself.

```{literalinclude} ../../../../examples/tutorial/media/images.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![19. Embed an image](../../../../examples/output/tutorial/media/images.svg)

[Complete runnable example](../../../../examples/tutorial/media/images.py)

Left to right: contain preserves all pixels and leaves blank space; cover
fills the square and clips excess content; stretch fills it with distortion.
All modes center the image. Position is the viewport's lower-left corner;
width and height are millimeters, not pixel counts. The source is twice as
wide as it is tall, making the three behaviors visible.

Image captures file bytes immediately, so later file edits do not affect it.
Call its rotation/scale methods directly or include it in a Group. Its bounds
are the explicit viewport, including contain-mode blank space.

SVG embeds the bytes. Saving TikZ creates a sibling `<stem>-assets` directory;
move that directory together with the TeX file. Source returned by render
references a temporary cached asset instead. No SVG/PDF import, EXIF rotation,
DPI-based sizing, or color-profile conversion is performed.

Try a tall viewport or rotate the image directly.

---

[Part contents](index.md)
