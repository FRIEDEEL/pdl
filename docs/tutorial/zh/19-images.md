# 19. 嵌入图片

Image 接受本地 PNG 或 JPEG。本例 image_file 指向[四色源图](../../../examples/tutorial/media/quadrants.png)，
完整脚本在自身目录中定位该文件。

```{literalinclude} ../../../examples/tutorial/media/images.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![19. 嵌入图片](../../../examples/output/tutorial/media/images.svg)

[完整可运行示例](../../../examples/tutorial/media/images.py)

从左到右：contain 保留全部内容并留白；cover 铺满方框并裁去超出部分；stretch 拉伸铺满。
三种模式都居中放置。position 表示视口左下角，width 和 height 使用毫米，不是像素。
源图宽高比为 2:1，因此可以清楚看到区别。

Image 创建时立即捕获文件内容，后续文件修改不影响它。需要旋转或缩放时包进 Entity，
也可以加入 Group。边界始终是显式视口，包含 contain 模式下的空白。

SVG 内嵌图片字节。保存 TikZ 时生成同级的 `<stem>-assets` 目录，移动 TeX 时需一并移动它。
render 返回的源码则引用临时缓存资源。目前不导入 SVG／PDF，不处理 EXIF 旋转、DPI 尺寸或色彩配置转换。

试试较高的视口，或旋转包含图片的 Entity。
