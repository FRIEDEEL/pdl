# 构建文档与示例

用 pyenv 选择 Python 3.12 或以上版本，再使用 uv 管理项目环境。
在仓库根目录运行 `uv sync --group docs`。运行时依赖为 fontTools 和 uharfbuzz；
文档使用 Sphinx、MyST、Napoleon 和 Furo。

SVG 文字需要可用的系统字体或显式 Font 文件。TeX 示例和测量需要 XeLaTeX、dvisvgm，
以及 TikZ、standalone、amsmath、amssymb、fontspec 和示例使用的字体。
SVG 原生文字引用已安装字体；`examples/_shared/config.py` 显式选择示例字体。

```sh
uv run python -m examples.tutorial.render_all
uv run python -m examples.tools.render_all --tikz-mode pdf
uv run --group docs python docs/build.py
```

构建脚本先运行一次教程和关联案例的生成器，再分别构建中英文站点。
Sphinx 警告视为构建失败。打开 `docs/_build/html/index.html` 选择语言，
也可直接打开中文首页 `docs/_build/html/zh/index_zh.html`
或英文首页 `docs/_build/html/en/index.html`。
两种语言拥有各自的目录、界面语言和搜索索引，每个翻译页面链接到对应的另一语言页面。
API 参考仅在英文站点生成，中文站点提供明确标注为英文的链接。

英文教程位于 `tutorial/en`，对应中文教程位于 `tutorial/zh`。
顶层中文页面使用 `_zh.md` 后缀，中文首页为 `index_zh.md`。
语言切换根据对应文件名生成。两种语言共用示例源码和图片。
修改课程时同步更新可运行源码并重新生成实际输出；变换示例保留对照图。
生成的图片和构建产物不加入 Git。

如果需要单独构建一种语言，设置 `PDL_DOCS_LANGUAGE` 为 `en` 或 `zh`，
并保持两个输出目录独立：

```sh
PDL_DOCS_LANGUAGE=en uv run --group docs sphinx-build -W --keep-going -b html docs docs/_build/html/en
PDL_DOCS_LANGUAGE=zh uv run --group docs sphinx-build -W --keep-going -b html docs docs/_build/html/zh
```

以上单独构建命令都会重新生成示例。`docs/build.py` 在英文构建中生成示例，
随后中文构建显式复用这些产物。

```sh
uv run ruff check .
uv run ruff format --check .
uv run pyright
uv run pytest
uv build
```

当前实现位于 `src/pdl`，测试在 `tests` 下镜像模块结构。
旧实现和测试保留在 Git 历史中。面向读者的示例也参与严格类型检查。
缺少外部工具或字体时，集成测试会报告跳过；应如实说明这些限制。
