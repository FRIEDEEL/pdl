# Learn to draw with pdl

Start with a box saying “Hello world”, then draw and color a few shapes.
Each step includes a complete Python script and its resulting SVG image.
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

The code blocks are complete copies of the linked example files. When editing
a lesson, keep its code block and example source in sync.

[中文版](../zh/index.md)
