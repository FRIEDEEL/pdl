# SVG、TikZ 与 PDF 输出

后端接收捕获的 Entity，根据当前 Geometry 和 Style 编码。图示的几何、连接端口和摆放由 Python 数值确定；
TikZ 的文字节点用于已确定基线处的排版，不承担图示布局或返回位置的计算。

`canvas.render()` 返回 SVG，`canvas.render("tikz")` 返回独立 LaTeX 文档；
`standalone=False` 返回可嵌入片段，配合 `canvas.latex_preamble()` 使用。
保存时明确指定 `backend="tikz"`，扩展名本身不切换后端。

`tikz_mode="tex"` 仅保存最终源码；auto 在编译器存在时编译，pdf 要求编译成功。
TeX 对象的测量仍可能在提交时调用 XeLaTeX／dvisvgm，即使最终只需要源码。
默认最终编译器是 XeLaTeX，普通原生字体需要 fontspec；纯几何也可选择适用的其他 LaTeX 引擎。
编译失败保留源码并报告日志，默认把辅助文件放在临时目录。

图片在 SVG 中内嵌，在 TikZ 保存时复制为源码旁的内容寻址资源。移动输出时一起移动资源目录。
渐变编码为矢量填充。普通 Text 在保持朝向手性的相似变换下保留原生表达；TeX 平移／旋转保留源码，
TeX 缩放及其他文字变形转为已测量的轮廓。复杂或彩色 TeX SVG 可原生嵌入，
无法保持内容的路径转换会明确拒绝，包括视口 fit 缩放时。

字体环境和原生排版可能造成 SVG／LaTeX 栅格差异。尺寸和位置使用已测量的资源策略，
但不保证逐像素一致，也不以生成源码的可读性限制几何表达。

[教程](tutorial/zh/06-output/index.md)
