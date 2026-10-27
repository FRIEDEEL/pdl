# Learn to draw with pdl

Start with a box saying “Hello world”, then draw and color a few shapes.
Each step includes drawing code, its resulting SVG image, and a link to a complete runnable example.
No knowledge of pdl's rendering internals is needed.

1. [Your first picture](01-hello-world.md)
2. [Basic shapes](02-shapes.md)
3. [Outlines and fills](03-stroke-and-fill.md)

Start with chapter 1 for environment setup. Run commands from the repository
root. Each script is independent and saves its image under
`examples/output/tutorial/basics/`. Run it before viewing its image in a local
Markdown preview. Generated images are not tracked by Git.

To generate all seven images at once:

```sh
uv run python -m examples.tutorial.render_all
```

After chapter 1, code blocks show only the drawing code. Saving files and
choosing output paths are omitted; the linked examples include those steps.
To save a drawing yourself, append `canvas.save("drawing.svg")` as in chapter 1.
When editing a lesson, keep its drawing code in sync with the example source.

[中文版](../zh/index.md)
